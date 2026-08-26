import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models import get_db, models
from resources.utils import verify_authentication
from configs.base_config import CommonWords

router = APIRouter()

STATUS = CommonWords.STATUS
UNSTATUS = CommonWords.UNSTATUS


def gen_code(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


def _auth(request: Request):
    user_id, role_id, company_id, token = verify_authentication(request)
    if not company_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")
    return user_id, role_id, company_id


def _round(value: float) -> float:
    return round(value, 2)


# =====================================================
# SCHEMAS
# =====================================================
class BillGenerateIn(BaseModel):
    cgst_percentage: float = 0
    sgst_percentage: float = 0
    service_charge_percentage: float = 0
    discount_type: Optional[str] = None
    discount_value: float = 0


class PaymentIn(BaseModel):
    payment_method_id: int
    paid_amount: float
    payment_reference: Optional[str] = None
    remarks: Optional[str] = None


class BillCancelIn(BaseModel):
    reason: str


class SplitByPersonIn(BaseModel):
    split_type: str = "By Person"
    number_of_people: int


class PaymentMethodIn(BaseModel):
    method_name: str


# =====================================================
# PAYMENT METHODS
# =====================================================
@router.post("/payment_method", status_code=status.HTTP_201_CREATED)
def create_payment_method(payload: PaymentMethodIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    row = models.BarPaymentMethod(created_by=user_id, company_id=company_id, **payload.dict())
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"status": "success", "data": {"id": row.id, "method_name": row.method_name}}


@router.get("/payment_method", status_code=status.HTTP_200_OK)
def list_payment_methods(request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    rows = db.query(models.BarPaymentMethod).filter(models.BarPaymentMethod.company_id == company_id, models.BarPaymentMethod.status == STATUS).all()
    return {"status": "success", "count": len(rows), "data": rows}


# =====================================================
# BILL GENERATION
# =====================================================
@router.post("/bill/generate/{order_id}", status_code=status.HTTP_201_CREATED)
def generate_bill(order_id: int, payload: BillGenerateIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    order = db.query(models.BarOrder).filter(models.BarOrder.id == order_id, models.BarOrder.company_id == company_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    existing = db.query(models.BarBill).filter(models.BarBill.order_id == order_id, models.BarBill.bill_status != "Cancelled").first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A bill already exists for this order")

    order_items = db.query(models.BarOrderItem).filter(models.BarOrderItem.order_id == order_id, models.BarOrderItem.status == STATUS).all()
    if not order_items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order has no billable items")

    try:
        sub_total = sum((i.price or 0) * (i.quantity or 0) for i in order_items)

        cgst_amount = _round(sub_total * (payload.cgst_percentage or 0) / 100)
        sgst_amount = _round(sub_total * (payload.sgst_percentage or 0) / 100)
        service_charge_amount = _round(sub_total * (payload.service_charge_percentage or 0) / 100)

        if payload.discount_type == "Percentage":
            discount_amount = _round(sub_total * (payload.discount_value or 0) / 100)
        else:
            discount_amount = _round(payload.discount_value or 0)

        raw_total = sub_total + cgst_amount + sgst_amount + service_charge_amount - discount_amount
        grand_total = round(raw_total)
        round_off = _round(grand_total - raw_total)

        now = datetime.now()
        bill = models.BarBill(
            bill_number=gen_code("BBILL"),
            bill_date=now.date(),
            bill_time=now.time(),
            order_id=order.id,
            order_number=order.order_number,
            table_id=order.table_id,
            table_code=order.table_code,
            guest_id=order.guest_id,
            guest_name=order.guest_name,
            guest_mobile=order.guest_mobile,
            sub_total=sub_total,
            cgst_percentage=payload.cgst_percentage,
            cgst_amount=cgst_amount,
            sgst_percentage=payload.sgst_percentage,
            sgst_amount=sgst_amount,
            service_charge_percentage=payload.service_charge_percentage,
            service_charge_amount=service_charge_amount,
            discount_type=payload.discount_type,
            discount_value=payload.discount_value,
            discount_amount=discount_amount,
            round_off=round_off,
            grand_total=grand_total,
            bill_status="Open",
            payment_status="Pending",
            created_by=user_id,
            company_id=company_id,
        )
        db.add(bill)
        db.flush()

        for i in order_items:
            menu = db.query(models.BarMenuItem).filter(models.BarMenuItem.id == i.menu_id).first()
            amount = (i.price or 0) * (i.quantity or 0)
            db.add(
                models.BarBillItem(
                    bill_id=bill.id,
                    order_item_id=i.id,
                    menu_id=i.menu_id,
                    item_name=menu.item_name if menu else "Item",
                    quantity=i.quantity,
                    rate=i.price,
                    amount=amount,
                    tax_amount=_round(amount * ((payload.cgst_percentage or 0) + (payload.sgst_percentage or 0)) / 100),
                    created_by=user_id,
                    company_id=company_id,
                )
            )

        order.payment_status = "Pending"
        db.commit()
        db.refresh(bill)
        return {"status": "success", "data": {"id": bill.id, "bill_number": bill.bill_number, "grand_total": bill.grand_total}}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/bill", status_code=status.HTTP_200_OK)
def list_bills(
    request: Request,
    payment_status: Optional[str] = Query(None),
    table_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    user_id, role_id, company_id = _auth(request)
    q = db.query(models.BarBill).filter(models.BarBill.company_id == company_id, models.BarBill.status == STATUS)
    if payment_status:
        q = q.filter(models.BarBill.payment_status == payment_status)
    if table_id is not None:
        q = q.filter(models.BarBill.table_id == table_id)
    rows = q.order_by(models.BarBill.id.desc()).all()
    return {"status": "success", "count": len(rows), "data": rows}


@router.get("/bill/{bill_id}", status_code=status.HTTP_200_OK)
def get_bill(bill_id: int, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    bill = db.query(models.BarBill).filter(models.BarBill.id == bill_id, models.BarBill.company_id == company_id).first()
    if not bill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bill not found")
    items = db.query(models.BarBillItem).filter(models.BarBillItem.bill_id == bill_id).all()
    payments = db.query(models.BarBillPayment).filter(models.BarBillPayment.bill_id == bill_id).all()
    return {"status": "success", "data": {**bill.__dict__, "items": items, "payments": payments}}


# =====================================================
# PAYMENTS
# =====================================================
@router.post("/bill/{bill_id}/payment", status_code=status.HTTP_201_CREATED)
def record_payment(bill_id: int, payload: PaymentIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    bill = db.query(models.BarBill).filter(models.BarBill.id == bill_id, models.BarBill.company_id == company_id).first()
    if not bill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bill not found")
    if bill.bill_status == "Cancelled":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot pay a cancelled bill")
    if payload.paid_amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="paid_amount must be greater than zero")

    # Overpayment guard. Without it this endpoint accepted any amount: paying
    # 50,000 against a 500 bill was recorded in full, and a bill already marked
    # Paid could be paid again, leaving total_paid above grand_total with no
    # record of the excess. The hotel side already refuses this
    # (HotelServices reservation_pay_due_amount); billing was newer code that
    # never got the same check, and the `max(..., 0)` clamp on the balance in
    # the response below was hiding the result rather than preventing it.
    already_paid = sum(
        p.paid_amount or 0
        for p in db.query(models.BarBillPayment)
        .filter(models.BarBillPayment.bill_id == bill.id, models.BarBillPayment.payment_status == "Success")
        .all()
    )
    outstanding = (bill.grand_total or 0) - already_paid
    if outstanding <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This bill is already fully paid",
        )
    if payload.paid_amount > outstanding:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"paid_amount exceeds the outstanding balance of {outstanding}",
        )

    try:
        now = datetime.now()
        payment = models.BarBillPayment(
            bill_id=bill.id,
            payment_method_id=payload.payment_method_id,
            paid_amount=payload.paid_amount,
            payment_reference=payload.payment_reference,
            payment_date=now.date(),
            payment_time=now.time(),
            payment_status="Success",
            remarks=payload.remarks,
            created_by=user_id,
            company_id=company_id,
        )
        db.add(payment)
        db.flush()

        total_paid = sum(
            p.paid_amount
            for p in db.query(models.BarBillPayment).filter(models.BarBillPayment.bill_id == bill.id, models.BarBillPayment.payment_status == "Success").all()
        )

        if total_paid >= bill.grand_total:
            bill.payment_status = "Paid"
            bill.bill_status = "Paid"
        elif total_paid > 0:
            bill.payment_status = "Partial"

        order = db.query(models.BarOrder).filter(models.BarOrder.id == bill.order_id).first()
        if order and bill.payment_status == "Paid" and order.order_status != "Completed":
            order.payment_status = "Paid"
            order.order_status = "Completed"
            if order.table_code:
                table = db.query(models.BarTable).filter(models.BarTable.table_code == order.table_code, models.BarTable.company_id == company_id).first()
                if table:
                    table.table_status = "Cleaning"
                    table.current_order_id = None
                    table.updated_by = user_id

            guest = None
            if order.guest_id:
                guest = db.query(models.BarGuest).filter(models.BarGuest.id == order.guest_id, models.BarGuest.company_id == company_id).first()
            elif order.guest_mobile:
                guest = (
                    db.query(models.BarGuest)
                    .filter(models.BarGuest.mobile == order.guest_mobile, models.BarGuest.company_id == company_id, models.BarGuest.status == STATUS)
                    .first()
                )
            if guest:
                db.add(models.BarGuestVisitHistory(
                    guest_id=guest.id,
                    visit_date=now.date(),
                    order_id=order.id,
                    bill_id=bill.id,
                    visit_type=order.order_type,
                    total_amount=bill.grand_total,
                    company_id=company_id,
                ))
                guest.loyalty_points = (guest.loyalty_points or 0) + int((bill.grand_total or 0) // 100)
                guest.updated_by = user_id

        db.commit()
        return {
            "status": "success",
            "data": {"id": payment.id, "total_paid": total_paid, "balance": max(bill.grand_total - total_paid, 0), "payment_status": bill.payment_status},
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/bill/{bill_id}/cancel", status_code=status.HTTP_200_OK)
def cancel_bill(bill_id: int, payload: BillCancelIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    bill = db.query(models.BarBill).filter(models.BarBill.id == bill_id, models.BarBill.company_id == company_id).first()
    if not bill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bill not found")
    if bill.payment_status == "Paid":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot cancel a bill that is already paid")
    bill.bill_status = "Cancelled"
    bill.remarks = f"Cancelled: {payload.reason}"
    bill.updated_by = user_id
    db.commit()
    return {"status": "success", "message": "Bill cancelled"}


# =====================================================
# SPLIT BILL (even split by person)
# =====================================================
@router.post("/bill/{bill_id}/split", status_code=status.HTTP_201_CREATED)
def split_bill_by_person(bill_id: int, payload: SplitByPersonIn, request: Request, db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    bill = db.query(models.BarBill).filter(models.BarBill.id == bill_id, models.BarBill.company_id == company_id).first()
    if not bill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bill not found")
    if payload.number_of_people < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="number_of_people must be at least 2")
    if bill.payment_status == "Paid":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bill is already paid")

    try:
        split = models.BarBillSplit(
            original_bill_id=bill.id,
            split_type=payload.split_type,
            split_count=payload.number_of_people,
            created_by=user_id,
            company_id=company_id,
        )
        db.add(split)
        db.flush()

        share = _round(bill.grand_total / payload.number_of_people)
        child_bills = []
        remaining = bill.grand_total
        for n in range(1, payload.number_of_people + 1):
            amount = share if n < payload.number_of_people else _round(remaining)
            remaining -= amount

            child = models.BarBill(
                bill_number=gen_code("BBILL"),
                bill_date=bill.bill_date,
                bill_time=bill.bill_time,
                order_id=bill.order_id,
                order_number=bill.order_number,
                table_id=bill.table_id,
                table_code=bill.table_code,
                guest_name=f"{bill.guest_name or 'Guest'} (split {n}/{payload.number_of_people})",
                sub_total=amount,
                grand_total=amount,
                bill_status="Open",
                payment_status="Pending",
                remarks=f"Split from {bill.bill_number}",
                created_by=user_id,
                company_id=company_id,
            )
            db.add(child)
            db.flush()

            db.add(models.BarBillSplitDetail(split_id=split.id, child_bill_id=child.id, split_number=n, split_amount=amount, created_by=user_id, company_id=company_id))
            child_bills.append({"id": child.id, "bill_number": child.bill_number, "amount": amount})

        bill.bill_status = "Cancelled"
        bill.remarks = f"Split into {payload.number_of_people} bills"
        db.commit()
        return {"status": "success", "data": {"split_id": split.id, "child_bills": child_bills}}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
