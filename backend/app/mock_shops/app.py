from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from backend.app.mock_shops.data import PRODUCTS

router = APIRouter(prefix="/mock", tags=["Mock Ecommerce Shops"])

STORES_INFO = {
    "dealnest": {"name": "DealNest India", "quirk": "Hidden ₹500 promo coupon 'DEAL500' in footer"},
    "flashkart": {"name": "FlashKart Mega Store", "quirk": "Deceptive Fake MRP discount framing"},
    "electrobazaar": {"name": "ElectroBazaar Direct", "quirk": "Drip pricing fee injection at final checkout"}
}

def get_product(product_id: str):
    for p in PRODUCTS:
        if p["id"] == product_id:
            return p
    return None

@router.get("/", response_class=HTMLResponse)
async def mock_index(request: Request):
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Mock Shops Hub - Multiverse Browser</title>
    <style>body { font-family: system-ui, sans-serif; max-width: 800px; margin: 40px auto; line-height: 1.6; }
    .store-card { border: 1px solid #ccc; border-radius: 8px; padding: 16px; margin-bottom: 16px; }
    h1 { color: #1e293b; }
    a { color: #2563eb; text-decoration: none; font-weight: bold; }
    </style></head>
    <body>
        <h1>🛒 Multiverse Browser - Target Mock Stores</h1>
        <p>Three seeded stores designed with realistic ecommerce patterns & dark patterns for reproducible evaluation.</p>
    """
    for store_id, info in STORES_INFO.items():
        html += f"""
        <div class="store-card">
            <h2>{info['name']} (<code>/mock/{store_id}</code>)</h2>
            <p><strong>Planted Quirk:</strong> {info['quirk']}</p>
            <ul>
        """
        for p in PRODUCTS:
            html += f'<li><a href="/mock/{store_id}/{p["id"]}">{p["name"]} - View Listing</a></li>'
        html += "</ul></div>"
    html += "</body></html>"
    return HTMLResponse(content=html)

@router.get("/{store_id}/{product_id}", response_class=HTMLResponse)
async def product_page(store_id: str, product_id: str):
    if store_id not in STORES_INFO:
        raise HTTPException(status_code=404, detail="Store not found")
    product = get_product(product_id)
    if not product or store_id not in product["stores"]:
        raise HTTPException(status_code=404, detail="Product not found in this store")
    
    store_data = product["stores"][store_id]
    store_meta = STORES_INFO[store_id]
    
    # Render realistic product page with store-specific markup
    hidden_coupon_html = ""
    if store_id == "dealnest" and store_data.get("hidden_coupon"):
        hidden_coupon_html = f"""
        <div id="promo-banner" style="margin-top: 30px; background: #fef08a; padding: 10px; border-left: 4px solid #ca8a04; font-size: 13px;">
            🎉 Secret Member Perks: Use coupon code <strong id="coupon-code">{store_data['hidden_coupon']}</strong> for ₹500 off at checkout!
        </div>
        """

    fake_mrp_html = ""
    if store_id == "flashkart":
        fake_mrp_html = f"""
        <div id="mrp-section" style="margin: 10px 0;">
            <span style="text-decoration: line-through; color: #888;">M.R.P.: ₹{store_data['claimed_mrp']}</span>
            <span style="color: #16a34a; font-weight: bold; margin-left: 8px;">(64% OFF - LIMITED TIME DEAL!)</span>
            <p style="font-size: 11px; color: #666;">*MRP claimed by marketplace seller, not manufacturer verified.</p>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{product['name']} - {store_meta['name']}</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f8fafc; color: #0f172a; margin: 0; padding: 20px; }}
            .container {{ max-width: 900px; margin: 0 auto; background: #fff; border-radius: 12px; padding: 30px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
            .store-header {{ border-bottom: 2px solid #e2e8f0; padding-bottom: 12px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; }}
            .product-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }}
            .img-box {{ background: #f1f5f9; border-radius: 8px; height: 260px; display: flex; align-items: center; justify-content: center; font-size: 48px; }}
            .price-tag {{ font-size: 32px; font-weight: 800; color: #0f172a; }}
            .btn-checkout {{ background: #2563eb; color: #fff; border: none; padding: 12px 24px; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; text-decoration: none; display: inline-block; margin-top: 16px; }}
            .btn-checkout:hover {{ background: #1d4ed8; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="store-header">
                <h2>{store_meta['name']}</h2>
                <span style="font-size: 12px; background: #e2e8f0; padding: 4px 8px; border-radius: 4px;">Store ID: {store_id}</span>
            </div>
            <div class="product-grid">
                <div class="img-box">🎧</div>
                <div>
                    <h1 id="product-title" style="font-size: 24px; margin-top: 0;">{product['name']}</h1>
                    <p style="color: #64748b;">Specs: {product['specs']}</p>
                    <p>⭐ <strong>{product['rating']}</strong> / 5.0 ({product['reviews_count']} reviews) | Warranty: {product['warranty_months']} months</p>
                    
                    {fake_mrp_html}
                    
                    <div class="price-tag">
                        ₹<span id="displayed-price">{store_data['listed_price']}</span>
                    </div>
                    <p style="color: #16a34a; font-weight: 500;">✓ In Stock | Delivery in 2 Days</p>

                    <a class="btn-checkout" id="btn-proceed-checkout" href="/mock/{store_id}/{product_id}/checkout">Proceed to Checkout →</a>

                    {hidden_coupon_html}
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@router.get("/{store_id}/{product_id}/checkout", response_class=HTMLResponse)
async def checkout_page(store_id: str, product_id: str, coupon: str = ""):
    product = get_product(product_id)
    if not product or store_id not in product["stores"]:
        raise HTTPException(status_code=404, detail="Product not found")
    
    store_data = product["stores"][store_id]
    base_price = store_data["listed_price"]
    
    # Calculate Drip pricing fees if ElectroBazaar
    drip_fees_total = 0
    drip_breakdown_html = ""
    if store_id == "electrobazaar" and "drip_fees" in store_data:
        for fee_name, fee_val in store_data["drip_fees"].items():
            drip_fees_total += fee_val
            drip_breakdown_html += f"""
            <div style="display: flex; justify-content: space-between; color: #dc2626; font-size: 14px;">
                <span>⚠️ {fee_name.replace('_', ' ').title()}</span>
                <span>+ ₹{fee_val}</span>
            </div>
            """

    # Calculate discount if coupon applied
    discount = 0
    applied_coupon_text = ""
    if coupon.upper() in ["DEAL500", "SAVE500"] and store_id == "dealnest":
        discount = 500
        applied_coupon_text = "<span style='color: #16a34a;'>Coupon DEAL500 Applied (-₹500)</span>"
    elif coupon.upper() in ["SAVE200"] and store_id == "dealnest":
        discount = 200
        applied_coupon_text = "<span style='color: #16a34a;'>Coupon SAVE200 Applied (-₹200)</span>"

    final_landed_price = base_price + drip_fees_total - discount

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Checkout - {STORES_INFO[store_id]['name']}</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f1f5f9; padding: 30px; }}
            .checkout-box {{ max-width: 500px; margin: 0 auto; background: #fff; padding: 24px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            .line-item {{ display: flex; justify-content: space-between; margin-bottom: 12px; font-size: 15px; }}
            .total-line {{ display: flex; justify-content: space-between; border-top: 2px solid #0f172a; margin-top: 16px; padding-top: 16px; font-size: 20px; font-weight: bold; }}
            .coupon-box {{ margin: 20px 0; display: flex; gap: 8px; }}
            input[type=text] {{ flex: 1; padding: 8px 12px; border: 1px solid #cbd5e1; border-radius: 4px; }}
            button {{ background: #0f172a; color: #fff; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; }}
        </style>
    </head>
    <body>
        <div class="checkout-box">
            <h2>Order Summary (Checkout Step 2)</h2>
            <p><strong>Item:</strong> <span id="item-title">{product['name']}</span></p>
            <div class="line-item">
                <span>Base Listed Price:</span>
                <span>₹<span id="base-price">{base_price}</span></span>
            </div>
            {drip_breakdown_html}
            {f'<div class="line-item">{applied_coupon_text}</div>' if applied_coupon_text else ''}
            
            <div class="coupon-box">
                <form method="get" action="/mock/{store_id}/{product_id}/checkout" style="display: flex; width: 100%; gap: 8px;">
                    <input type="text" name="coupon" id="coupon-input" placeholder="Enter coupon code" value="{coupon}">
                    <button type="submit" id="btn-apply-coupon">Apply</button>
                </form>
            </div>

            <div class="total-line">
                <span>True Landed Price:</span>
                <span style="color: #2563eb;">₹<span id="final-landed-price">{final_landed_price}</span></span>
            </div>

            <div style="margin-top: 24px; font-size: 12px; color: #64748b; text-align: center;">
                🛡️ Read-Only Guardrail Active: Payment disabled in evaluation mode.
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
