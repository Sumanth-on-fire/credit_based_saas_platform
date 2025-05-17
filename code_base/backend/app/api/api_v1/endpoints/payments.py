from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.core.security import get_current_user
import razorpay
import hmac
import hashlib

router = APIRouter()

# Initialize Razorpay client
client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

@router.post("/create")
async def create_payment(
    amount: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new payment order."""
    try:
        # Create Razorpay order
        order = client.order.create({
            "amount": amount * 100,  # Convert to paise
            "currency": "INR",
            "receipt": f"receipt_{current_user.id}",
        })

        return {
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/verify")
async def verify_payment(
    order_id: str,
    payment_id: str,
    signature: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify the payment and add credits to user account."""
    try:
        # Verify signature
        params_dict = {
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature,
        }

        client.utility.verify_payment_signature(params_dict)

        # Add credits to user account (1 credit per 100 INR)
        amount = client.order.fetch(order_id)["amount"]
        credits_to_add = amount // 10000  # Convert from paise to INR, then to credits

        current_user.credits += credits_to_add
        db.commit()

        return {"message": "Payment verified successfully", "credits_added": credits_to_add}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 