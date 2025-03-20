from app.models.admin import AdminModel
import os
from app.core.security import hash_password


async def admin_init():
    try:
        admin = await AdminModel.find_one({"email": os.getenv("ADMIN_EMAIL")})
        if not admin:
            admin = AdminModel(
                email=os.getenv("ADMIN_EMAIL"),
                password=hash_password(os.getenv("ADMIN_PASSWORD")),
                role="admin"
            )
            await admin.insert()
    except Exception as e:
        print(e)
