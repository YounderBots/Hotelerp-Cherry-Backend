from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from models import get_db, models
from resources.utils import verify_authentication
from configs.base_config import CommonWords

router = APIRouter()

STATUS = CommonWords.STATUS


def _auth(request: Request):
    user_id, role_id, company_id, token = verify_authentication(request)
    if not company_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")
    return user_id, role_id, company_id


def _day(report_date: Optional[date]) -> date:
    return report_date or date.today()


# All reports are computed live from the transactional tables rather than the
# pre-aggregated report tables, so they reflect real data with no ETL step required.


@router.get("/reports/daily_sales", status_code=status.HTTP_200_OK)
def daily_sales(request: Request, report_date: Optional[date] = Query(None), db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    d = _day(report_date)

    bills = (
        db.query(models.RestaurantBill)
        .filter(models.RestaurantBill.company_id == company_id, models.RestaurantBill.bill_date == d, models.RestaurantBill.bill_status != "Cancelled")
        .all()
    )
    total_bills = len(bills)
    total_sales = sum(b.sub_total or 0 for b in bills)
    total_tax = sum((b.cgst_amount or 0) + (b.sgst_amount or 0) + (b.igst_amount or 0) for b in bills)
    total_discount = sum(b.discount_amount or 0 for b in bills)
    total_service_charge = sum(b.service_charge_amount or 0 for b in bills)
    grand_total = sum(b.grand_total or 0 for b in bills)

    total_orders = (
        db.query(func.count(models.RestaurantOrder.id))
        .filter(models.RestaurantOrder.company_id == company_id, models.RestaurantOrder.order_date == d)
        .scalar()
    )

    return {
        "status": "success",
        "data": {
            "report_date": d,
            "total_orders": total_orders,
            "total_bills": total_bills,
            "total_sales": round(total_sales, 2),
            "total_tax": round(total_tax, 2),
            "total_discount": round(total_discount, 2),
            "total_service_charge": round(total_service_charge, 2),
            "grand_total": round(grand_total, 2),
        },
    }


@router.get("/reports/item_sales", status_code=status.HTTP_200_OK)
def item_sales(request: Request, report_date: Optional[date] = Query(None), db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    d = _day(report_date)

    rows = (
        db.query(
            models.RestaurantBillItem.menu_id,
            models.RestaurantBillItem.item_name,
            func.sum(models.RestaurantBillItem.quantity).label("quantity_sold"),
            func.sum(models.RestaurantBillItem.amount).label("total_amount"),
        )
        .join(models.RestaurantBill, models.RestaurantBill.id == models.RestaurantBillItem.bill_id)
        .filter(models.RestaurantBill.company_id == company_id, models.RestaurantBill.bill_date == d, models.RestaurantBill.bill_status != "Cancelled")
        .group_by(models.RestaurantBillItem.menu_id, models.RestaurantBillItem.item_name)
        .order_by(func.sum(models.RestaurantBillItem.amount).desc())
        .all()
    )
    data = [{"menu_id": r.menu_id, "item_name": r.item_name, "quantity_sold": int(r.quantity_sold or 0), "total_amount": round(r.total_amount or 0, 2)} for r in rows]
    return {"status": "success", "count": len(data), "data": data}


@router.get("/reports/category_sales", status_code=status.HTTP_200_OK)
def category_sales(request: Request, report_date: Optional[date] = Query(None), db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    d = _day(report_date)

    rows = (
        db.query(
            models.RestaurantMenu.category_id,
            func.sum(models.RestaurantBillItem.quantity).label("total_quantity"),
            func.sum(models.RestaurantBillItem.amount).label("total_sales"),
        )
        .join(models.RestaurantBillItem, models.RestaurantBillItem.menu_id == models.RestaurantMenu.id)
        .join(models.RestaurantBill, models.RestaurantBill.id == models.RestaurantBillItem.bill_id)
        .filter(models.RestaurantBill.company_id == company_id, models.RestaurantBill.bill_date == d, models.RestaurantBill.bill_status != "Cancelled")
        .group_by(models.RestaurantMenu.category_id)
        .all()
    )
    category_ids = [r.category_id for r in rows]
    categories = db.query(models.MenuCategory).filter(models.MenuCategory.id.in_(category_ids)).all() if category_ids else []
    cat_by_id = {c.id: c for c in categories}

    data = [
        {
            "category_id": r.category_id,
            "category_name": cat_by_id.get(r.category_id).category_name if cat_by_id.get(r.category_id) else None,
            "total_quantity": int(r.total_quantity or 0),
            "total_sales": round(r.total_sales or 0, 2),
        }
        for r in rows
    ]
    return {"status": "success", "count": len(data), "data": data}


@router.get("/reports/payment_mode", status_code=status.HTTP_200_OK)
def payment_mode_report(request: Request, report_date: Optional[date] = Query(None), db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    d = _day(report_date)

    rows = (
        db.query(
            models.PaymentMethod.method_name,
            func.sum(models.RestaurantBillPayment.paid_amount).label("total_amount"),
        )
        .join(models.RestaurantBillPayment, models.RestaurantBillPayment.payment_method_id == models.PaymentMethod.id)
        .filter(
            models.RestaurantBillPayment.company_id == company_id,
            models.RestaurantBillPayment.payment_date == d,
            models.RestaurantBillPayment.payment_status == "Success",
        )
        .group_by(models.PaymentMethod.method_name)
        .all()
    )
    data = [{"payment_method": r.method_name, "total_amount": round(r.total_amount or 0, 2)} for r in rows]
    return {"status": "success", "count": len(data), "data": data}


@router.get("/reports/staff_performance", status_code=status.HTTP_200_OK)
def staff_performance(request: Request, report_date: Optional[date] = Query(None), db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    d = _day(report_date)

    shifts = (
        db.query(models.RestaurantStaffAssignment)
        .filter(models.RestaurantStaffAssignment.company_id == company_id, models.RestaurantStaffAssignment.shift_date == d)
        .all()
    )
    data = [
        {
            "employee_id": s.employee_id,
            "employee_name": s.employee_name,
            "role": s.role,
            "sales_target": s.sales_target,
            "actual_sales": s.actual_sales,
            "shift_status": s.shift_status,
        }
        for s in shifts
    ]
    return {"status": "success", "count": len(data), "data": data}


@router.get("/reports/kitchen_performance", status_code=status.HTTP_200_OK)
def kitchen_performance(request: Request, report_date: Optional[date] = Query(None), db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    d = _day(report_date)

    kots = (
        db.query(models.KitchenOrderTicket)
        .filter(models.KitchenOrderTicket.company_id == company_id, func.date(models.KitchenOrderTicket.created_at) == d)
        .all()
    )
    by_kitchen = {}
    for k in kots:
        entry = by_kitchen.setdefault(k.kitchen_id, {"total_kots": 0, "completed_kots": 0, "prep_seconds": [], })
        entry["total_kots"] += 1
        if k.kot_status == "Completed":
            entry["completed_kots"] += 1
            if k.acknowledged_at and k.completed_at:
                entry["prep_seconds"].append((k.completed_at - k.acknowledged_at).total_seconds())

    kitchen_ids = list(by_kitchen.keys())
    kitchens = db.query(models.Kitchen).filter(models.Kitchen.id.in_(kitchen_ids)).all() if kitchen_ids else []
    kitchen_by_id = {kk.id: kk for kk in kitchens}

    data = []
    for kid, stats in by_kitchen.items():
        avg_prep = round(sum(stats["prep_seconds"]) / len(stats["prep_seconds"]) / 60, 1) if stats["prep_seconds"] else None
        data.append(
            {
                "kitchen_id": kid,
                "kitchen_name": kitchen_by_id.get(kid).kitchen_name if kitchen_by_id.get(kid) else None,
                "total_kots": stats["total_kots"],
                "completed_kots": stats["completed_kots"],
                "avg_preparation_time_minutes": avg_prep,
            }
        )
    return {"status": "success", "count": len(data), "data": data}


@router.get("/reports/table_turnover", status_code=status.HTTP_200_OK)
def table_turnover(request: Request, report_date: Optional[date] = Query(None), db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    d = _day(report_date)

    rows = (
        db.query(models.RestaurantOrder.table_code, func.count(models.RestaurantOrder.id).label("orders_count"))
        .filter(models.RestaurantOrder.company_id == company_id, models.RestaurantOrder.order_date == d, models.RestaurantOrder.table_code.isnot(None))
        .group_by(models.RestaurantOrder.table_code)
        .all()
    )
    data = [{"table_code": r.table_code, "orders_count": r.orders_count} for r in rows]
    return {"status": "success", "count": len(data), "data": data}


@router.get("/reports/average_check_size", status_code=status.HTTP_200_OK)
def average_check_size(request: Request, report_date: Optional[date] = Query(None), db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    d = _day(report_date)

    result = (
        db.query(func.count(models.RestaurantBill.id), func.sum(models.RestaurantBill.grand_total))
        .filter(models.RestaurantBill.company_id == company_id, models.RestaurantBill.bill_date == d, models.RestaurantBill.bill_status != "Cancelled")
        .first()
    )
    count, total = result[0] or 0, result[1] or 0
    average = round(total / count, 2) if count else 0
    return {"status": "success", "data": {"report_date": d, "bill_count": count, "total_sales": round(total, 2), "average_check_size": average}}


@router.get("/reports/cancelled_orders", status_code=status.HTTP_200_OK)
def cancelled_orders(request: Request, report_date: Optional[date] = Query(None), db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    d = _day(report_date)

    rows = (
        db.query(models.RestaurantOrder)
        .filter(models.RestaurantOrder.company_id == company_id, models.RestaurantOrder.order_date == d, models.RestaurantOrder.order_status == "Cancelled")
        .all()
    )
    return {"status": "success", "count": len(rows), "data": rows}
