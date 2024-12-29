from .office import router as office_router
from .refferal_sys import router as refferal_sys_router


async def worker_routers(dp):
    dp.include_router(office_router)
    dp.include_router(refferal_sys_router)
