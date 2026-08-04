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
        db.query(models.BarBill)
        .filter(models.BarBill.company_id == company_id, models.BarBill.bill_date == d, models.BarBill.bill_status != "Cancelled")
        .all()
    )
    total_bills = len(bills)
    total_sales = sum(b.sub_total or 0 for b in bills)
    total_tax = sum((b.cgst_amount or 0) + (b.sgst_amount or 0) for b in bills)
    total_discount = sum(b.discount_amount or 0 for b in bills)
    total_service_charge = sum(b.service_charge_amount or 0 for b in bills)
    grand_total = sum(b.grand_total or 0 for b in bills)

    total_orders = (
        db.query(func.count(models.BarOrder.id))
        .filter(models.BarOrder.company_id == company_id, models.BarOrder.order_date == d)
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
            models.BarBillItem.menu_id,
            models.BarBillItem.item_name,
            func.sum(models.BarBillItem.quantity).label("quantity_sold"),
            func.sum(models.BarBillItem.amount).label("total_amount"),
        )
        .join(models.BarBill, models.BarBill.id == models.BarBillItem.bill_id)
        .filter(models.BarBill.company_id == company_id, models.BarBill.bill_date == d, models.BarBill.bill_status != "Cancelled")
        .group_by(models.BarBillItem.menu_id, models.BarBillItem.item_name)
        .order_by(func.sum(models.BarBillItem.amount).desc())
        .all()
    )
    data = [{"menu_id": r.menu_id, "item_name": r.item_name, "quantity_sold": int(r.quantity_sold or 0), "total_amount": round(r.total_amount or 0, 2)} for r in rows]
    return {"status": "success", "count": len(data), "data": data}


@router.get("/reports/payment_mode", status_code=status.HTTP_200_OK)
def payment_mode_report(request: Request, report_date: Optional[date] = Query(None), db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    d = _day(report_date)

    rows = (
        db.query(
            models.BarPaymentMethod.method_name,
            func.sum(models.BarBillPayment.paid_amount).label("total_amount"),
        )
        .join(models.BarBillPayment, models.BarBillPayment.payment_method_id == models.BarPaymentMethod.id)
        .filter(
            models.BarBillPayment.company_id == company_id,
            models.BarBillPayment.payment_date == d,
            models.BarBillPayment.payment_status == "Success",
        )
        .group_by(models.BarPaymentMethod.method_name)
        .all()
    )
    data = [{"payment_method": r.method_name, "total_amount": round(r.total_amount or 0, 2)} for r in rows]
    return {"status": "success", "count": len(data), "data": data}


@router.get("/reports/staff_performance", status_code=status.HTTP_200_OK)
def staff_performance(request: Request, report_date: Optional[date] = Query(None), db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    d = _day(report_date)

    shifts = (
        db.query(models.BarStaffAssignment)
        .filter(models.BarStaffAssignment.company_id == company_id, models.BarStaffAssignment.shift_date == d)
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


@router.get("/reports/cancelled_orders", status_code=status.HTTP_200_OK)
def cancelled_orders(request: Request, report_date: Optional[date] = Query(None), db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    d = _day(report_date)

    rows = (
        db.query(models.BarOrder)
        .filter(models.BarOrder.company_id == company_id, models.BarOrder.order_date == d, models.BarOrder.order_status == "Cancelled")
        .all()
    )
    return {"status": "success", "count": len(rows), "data": rows}


@router.get("/reports/station_performance", status_code=status.HTTP_200_OK)
def station_performance(request: Request, report_date: Optional[date] = Query(None), db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    d = _day(report_date)

    tickets = (
        db.query(models.BarOrderTicket)
        .filter(models.BarOrderTicket.company_id == company_id, func.date(models.BarOrderTicket.created_at) == d)
        .all()
    )
    by_station = {}
    for t in tickets:
        entry = by_station.setdefault(t.station_id, {"total_bots": 0, "completed_bots": 0, "prep_seconds": []})
        entry["total_bots"] += 1
        if t.bot_status == "Completed":
            entry["completed_bots"] += 1
            if t.acknowledged_at and t.completed_at:
                entry["prep_seconds"].append((t.completed_at - t.acknowledged_at).total_seconds())

    station_ids = list(by_station.keys())
    stations = db.query(models.BarStation).filter(models.BarStation.id.in_(station_ids)).all() if station_ids else []
    station_by_id = {s.id: s for s in stations}

    data = []
    for sid, stats in by_station.items():
        avg_prep = round(sum(stats["prep_seconds"]) / len(stats["prep_seconds"]) / 60, 1) if stats["prep_seconds"] else None
        data.append(
            {
                "station_id": sid,
                "station_name": station_by_id.get(sid).station_name if station_by_id.get(sid) else None,
                "total_bots": stats["total_bots"],
                "completed_bots": stats["completed_bots"],
                "avg_preparation_time_minutes": avg_prep,
            }
        )
    return {"status": "success", "count": len(data), "data": data}


@router.get("/reports/table_turnover", status_code=status.HTTP_200_OK)
def table_turnover(request: Request, report_date: Optional[date] = Query(None), db: Session = Depends(get_db)):
    user_id, role_id, company_id = _auth(request)
    d = _day(report_date)

    rows = (
        db.query(models.BarOrder.table_code, func.count(models.BarOrder.id).label("orders_count"))
        .filter(models.BarOrder.company_id == company_id, models.BarOrder.order_date == d, models.BarOrder.table_code.isnot(None))
        .group_by(models.BarOrder.table_code)
        .all()
    )
    data = [{"table_code": r.table_code, "orders_count": r.orders_count} for r in rows]
    return {"status": "success", "count": len(data), "data": data}
