async def user_routers(dp):
    from .catalogue import router as catalogue_router
    from .balance import router as balance_router
    from .help import router as help_router

    dp.include_router(help_router)
    dp.include_router(catalogue_router)
    dp.include_router(balance_router)