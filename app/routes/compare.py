"""
Wallet Comparison Routes
"""
from flask import Blueprint, render_template, request
from app.database import get_session
from app.models import Wallet
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('compare', __name__, url_prefix='/compare')


@bp.route('/')
def compare_wallets():
    """Compare multiple wallets"""
    # Get wallet addresses from query params
    addresses = request.args.getlist('wallet')

    # Clean and validate addresses
    addresses = [addr.strip().lower() for addr in addresses if addr.strip()]
    addresses = addresses[:4]  # Max 4 wallets

    if not addresses:
        return render_template('compare.html', wallets=[], addresses=[])

    # Fetch wallets from database
    db = get_session()
    wallets = []

    for address in addresses:
        wallet = db.query(Wallet).filter_by(address=address).first()
        if wallet:
            wallets.append(wallet)

    return render_template('compare.html', wallets=wallets, addresses=addresses)
