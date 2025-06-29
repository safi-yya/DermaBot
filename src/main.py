from fastapi import FastAPI, HTTPException, Request
from db.connection import create_conn, close_db
from pydantic import BaseModel 
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import List, Optional
from datetime import datetime

app = FastAPI( title="DermaBot API" )

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class UserProfile(BaseModel):
    user_id: int
    name: str
    email: str
    birth_date: str
    skin_type: Optional[dict] = None
    skin_concerns: List[dict] = []
    age_category: Optional[dict] = None


class ProductResponse(BaseModel):
    """Frontend-compatible product model matching dermabot.js expectations"""
    product_id: int
    name: str
    category: str
    product_type: str
    anti_aging_subcategory: Optional[str] = None
    skin_types: List[str] = []
    skin_concerns: List[str] = []
    recommended_age: str = ""
    frequency: str  # 'daily', 'weekly', or number as string
    timeOfDay: str  # 'morning', 'evening', 'both'
    stepOrder: int
    totalVolumeMl: float
    usagePerUseMl: float
    usageLog: List[str] = []  # Array of ISO timestamp strings => usageLog: ["2025-06-25T21:00:00Z"]

class UsageLogRequest(BaseModel):
    volume_used: Optional[float] = None

@app.get("/api")
def read_root():
    return {"message": "Hello, DermaBot!"}

# Check healthy end_point
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        conn = create_conn()
        # Test database connection
        result = conn.run("SELECT 1")
        close_db(conn)
        return {
            "status": 200,
            "database": "connected",
            "message": "Healthy connection"
        }
    except Exception as e:
        return {
            "status": 500, 
            "database": "diskin_concernsonnected",
            "error": str(e)
        }
    

# get a full joined user_profile end points with skin_types, skin_concerns, and age_category_label
@app.get("/api/users/{user_id}/user_profile")
async def get_user_profile(user_id: int):
    """Get user name and full skin specification profile"""
    conn = create_conn()
    
    try:
        # Alap infók és age_category
        user_result = conn.run("""
            SELECT users.user_id, users.name, users.email, users.birth_date,
                   age_category.age_category_id, age_category.age_category_label
            FROM users
            LEFT JOIN age_category ON users.user_id = age_category.user_id
            WHERE users.user_id = %s
        """, (user_id,))
        
        if not user_result:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user_result[0]

        # Skin Types lekérdezése
        skin_types_result = conn.run("""
            SELECT st.skin_type_id, st.skin_type
            FROM user_skin_types ust
            JOIN skin_types st ON ust.skin_type_id = st.skin_type_id
            WHERE ust.user_id = %s
        """, (user_id,))
        
        user_skin = skin_types_result[0]
        print(f">>>> user skin type: {user_skin}")

        # Skin Concerns lekérdezése
        skin_concerns_result = conn.run("""
            SELECT sc.skin_concern_id, sc.skin_concern
            FROM user_skin_concerns usc
            JOIN skin_concerns sc ON usc.skin_concern_id = sc.skin_concern_id
            WHERE usc.user_id = %s
        """, (user_id,))

        user_skin_concerns = skin_concerns_result[0]
        print(f">>>> user skin concern: {user_skin_concerns}")
        
        # Összerakás
        user_profile = {
            "user_id": user_data[0],
            "name": user_data[1],
            "email": user_data[2],
            "birth_date": user_data[3].isoformat() if user_data[3] else None,
            "skin_types": [{"id": st[0], "name": st[1]} for st in skin_types_result],
            "skin_concerns": [{"id": sc[0], "name": sc[1]} for sc in skin_concerns_result],
            "age_category_id": user_data[6],
            "age_category_label": user_data[7]
        }
        
        return user_profile

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    finally:
        close_db(conn)

# get a full joined user_profile end points with skin_types, skin_concerns, and age_category_label
@app.get("/api/users/{user_id}/product_profile")
async def get_user_product_profile(user_id: int):
    """Get recommended products for user's profile with usage history"""
    conn = create_conn()
    
    try:
        # Get user's profile for matching
        user_profile_result = conn.run("""
            SELECT up.skin_type_id, up.skin_concern_id, ac.age_category_id
            FROM user_profile up
            LEFT JOIN age_category ac ON up.user_id = ac.user_id
            WHERE up.user_id = %s
        """, (user_id,))
        
        if not user_profile_result:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        user_skin_type_id, user_skin_concern_id, user_age_category_id = user_profile_result[0]
        
        # Get products that match user's profile
        products_result = conn.run("""
            SELECT DISTINCT p.product_id, p.name, p.product_type, p.product_category,
                   p.anti_aging_subcategory, p.frequency, p.timeOfDay, p.stepOrder,
                   p.totalVolumeMl, p.usagePerUseMl,
                   st.skin_type, sc.skin_concern, ac.age_category_label
            FROM products p
            LEFT JOIN product_profile pp ON p.product_id = pp.product_id
            LEFT JOIN skin_types st ON pp.skin_type_id = st.skin_type_id
            LEFT JOIN skin_concerns sc ON pp.skin_concern_id = sc.skin_concern_id
            LEFT JOIN age_category ac ON pp.age_category_id = ac.age_category_id
            WHERE (pp.skin_type_id = %s OR pp.skin_type_id IS NULL)
              AND (pp.skin_concern_id = %s OR pp.skin_concern_id IS NULL)
              AND (pp.age_category_id = %s OR pp.age_category_id IS NULL)
            ORDER BY p.stepOrder
        """, (user_skin_type_id, user_skin_concern_id, user_age_category_id))
        
        # Get usage logs for this user
        usage_result = conn.run("""
            SELECT product_id, used_at
            FROM user_product_usage
            WHERE user_id = %s AND is_in_routine = TRUE
            ORDER BY used_at DESC
        """, (user_id,))
        
        # Group usage by product_id
        usage_by_product = {}
        for usage in usage_result:
            product_id = usage[0]
            used_at = usage[1].isoformat() + "Z" if usage[1] else None
            if product_id not in usage_by_product:
                usage_by_product[product_id] = []
            if used_at:
                usage_by_product[product_id].append(used_at)
        
        # Build product responses
        products = []

        for row in products_result:
            product_id = row[0]
            product = {
                "product_id": product_id,
                "name": row[1],
                "product_type": row[2],
                "category": row[3],
                "anti_aging_subcategory": row[4],
                "frequency": row[5],
                "timeOfDay": row[6],
                "stepOrder": row[7],
                "totalVolumeMl": float(row[8]) if row[8] else 0.0,
                "usagePerUseMl": float(row[9]) if row[9] else 0.0,
                "skin_types": [row[10]] if row[10] else [],
                "skin_concerns": [row[11]] if row[11] else [],
                "recommended_age": row[12] if row[12] else "",
                "usageLog": usage_by_product.get(product_id, [])
            }
            products.append(product)
        
        return {"products": products}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    finally:
        close_db(conn)

@app.post("/api/users/{user_id}/products/{product_id}/usage")
async def log_product_usage(user_id: int, product_id: int, usage_data: UsageLogRequest):
    """Log product usage for a user"""
    conn = create_conn()
    
    try:
        # Verify user and product exist
        user_check = conn.run("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        if not user_check:
            raise HTTPException(status_code=404, detail="User not found")
        
        product_check = conn.run("SELECT product_id, usagePerUseMl FROM products WHERE product_id = %s", (product_id,))
        if not product_check:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Insert usage log
        conn.run("""
            INSERT INTO user_product_usage (user_id, product_id, used_at, is_in_routine)
            VALUES (%s, %s, CURRENT_TIMESTAMP, TRUE)
        """, (user_id, product_id))
        
        # Get updated usage count
        usage_count = conn.run("""
            SELECT COUNT(*) FROM user_product_usage
            WHERE user_id = %s AND product_id = %s AND is_in_routine = TRUE
        """, (user_id, product_id))[0][0]
        
        # Calculate remaining volume
        usage_per_use = float(product_check[0][1]) if product_check[0][1] else 0.0
        total_used = usage_count * usage_per_use
        
        # Get total volume
        total_volume_result = conn.run(
            "SELECT totalVolumeMl FROM products WHERE product_id = %s", 
            (product_id,)
        )
        total_volume = float(total_volume_result[0][0]) if total_volume_result[0][0] else 0.0
        remaining_volume = max(total_volume - total_used, 0.0)
        
        return {
            "message": "Usage logged successfully",
            "usage_count": usage_count,
            "total_used_ml": total_used,
            "remaining_volume_ml": remaining_volume,
            "logged_at": datetime.now().isoformat() + "Z"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    finally:
        close_db(conn)

# Additional helpful endpoints

@app.get("/api/skin-types")
async def get_skin_types():
    """Get all available skin types"""
    conn = create_conn()
    try:
        result = conn.run("SELECT skin_type_id, skin_type FROM skin_types ORDER BY skin_type")
        return {"skin_types": [{"id": row[0], "name": row[1]} for row in result]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        close_db(conn)

@app.get("/api/skin-concerns")
async def get_skin_concerns():
    """Get all available skin concerns"""
    conn = create_conn()
    try:
        result = conn.run("SELECT skin_concern_id, skin_concern FROM skin_concerns ORDER BY skin_concern")
        return {"skin_concerns": [{"id": row[0], "name": row[1]} for row in result]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        close_db(conn)

@app.get("/api/users/{user_id}/usage_stats")
async def get_user_usage_stats(user_id: int):
    """Get usage statistics for a user"""
    conn = create_conn()
    try:
        # Get usage stats by product
        result = conn.run("""
            SELECT p.name, COUNT(upu.log_id) as usage_count,
                   MAX(upu.used_at) as last_used,
                   p.totalVolumeMl, p.usagePerUseMl
            FROM user_product_usage upu
            JOIN products p ON upu.product_id = p.product_id
            WHERE upu.user_id = %s AND upu.is_in_routine = TRUE
            GROUP BY p.product_id, p.name, p.totalVolumeMl, p.usagePerUseMl
            ORDER BY usage_count DESC
        """, (user_id,))
        
        stats = []
        for row in result:
            total_used = row[1] * float(row[4]) if row[4] else 0
            total_volume = float(row[3]) if row[3] else 0
            remaining = max(total_volume - total_used, 0)
            
            stats.append({
                "product_name": row[0],
                "usage_count": row[1],
                "last_used": row[2].isoformat() + "Z" if row[2] else None,
                "total_volume_ml": total_volume,
                "total_used_ml": total_used,
                "remaining_volume_ml": remaining,
                "usage_percentage": (total_used / total_volume * 100) if total_volume > 0 else 0
            })
        
        return {"usage_stats": stats}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        close_db(conn)



 
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)