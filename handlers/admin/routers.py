# handlers/admin/routers.py

async def admin_routers(dp):
    from .admin_panel import router as admin_panel_router
    from .add_worker import router as add_worker_router
    from .wiev_workers import router as wiev_workers_router
    from .payment_req import router as payment_req_router
    from .replenish_user import router as replenish_user_router
    from .support_msg import router as support_msg_router

    dp.include_router(wiev_workers_router)
    dp.include_router(add_worker_router)
    dp.include_router(admin_panel_router)
    dp.include_router(payment_req_router)
    dp.include_router(support_msg_router)
    dp.include_router(replenish_user_router)
