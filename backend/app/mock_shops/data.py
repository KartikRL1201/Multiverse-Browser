"""
Seed data for the 3 mock ecommerce stores.
Products focused on Wireless Headphones category for reliable hackathon demo.
"""

PRODUCTS = [
    {
        "id": "soundpulse-500",
        "name": "SoundPulse Pro ANC Headphones",
        "category": "Headphones",
        "specs": "Active Noise Cancelling, 40hr Battery, Bluetooth 5.3",
        "rating": 4.5,
        "reviews_count": 840,
        "warranty_months": 12,
        "stores": {
            "dealnest": {
                "listed_price": 2799,
                "claimed_mrp": 3499,
                "shipping": 0,
                "hidden_coupon": "DEAL500", # Gives 500 off -> 2299 true
                "dark_patterns": []
            },
            "flashkart": {
                "listed_price": 2499,
                "claimed_mrp": 6999, # FAKE MRP / Fake 64% Discount
                "shipping": 50,
                "hidden_coupon": None,
                "dark_patterns": ["Fake MRP Inflation"]
            },
            "electrobazaar": {
                "listed_price": 2199, # Naive winner on page
                "claimed_mrp": 2999,
                "shipping": 0,
                "drip_fees": {
                    "convenience_fee": 199,
                    "mandatory_packaging": 149
                }, # Final Landed: 2199 + 199 + 149 = 2547
                "hidden_coupon": None,
                "dark_patterns": ["Drip Pricing at Checkout"]
            }
        }
    },
    {
        "id": "basswave-air",
        "name": "BassWave Air Wireless Earbuds",
        "category": "Headphones",
        "specs": "Deep Bass, IPX5 Water Resistant, 28hr Battery",
        "rating": 4.2,
        "reviews_count": 420,
        "warranty_months": 6,
        "stores": {
            "dealnest": {
                "listed_price": 1799,
                "claimed_mrp": 2499,
                "shipping": 0,
                "hidden_coupon": "SAVE200",
                "dark_patterns": []
            },
            "flashkart": {
                "listed_price": 1699,
                "claimed_mrp": 4999,
                "shipping": 40,
                "hidden_coupon": None,
                "dark_patterns": ["Fake MRP Inflation"]
            },
            "electrobazaar": {
                "listed_price": 1599,
                "claimed_mrp": 1999,
                "shipping": 0,
                "drip_fees": {"processing_fee": 220},
                "hidden_coupon": None,
                "dark_patterns": ["Drip Pricing at Checkout"]
            }
        }
    }
]
