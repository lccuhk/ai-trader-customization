"""
Routes Module

所有 API 路由定义入口。
"""

import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from config import CORS_ORIGINS
from routes_agent import register_agent_routes
from routes_challenges import register_challenge_routes
from routes_experiments import register_experiment_routes
from routes_market import register_market_routes
from routes_misc import register_misc_routes
from routes_research import register_research_routes
from routes_shared import RouteContext
from routes_signals import register_signal_routes
from routes_team_missions import register_team_mission_routes
from routes_trading import register_trading_routes
from routes_users import register_user_routes
from routes_extensions import router as extensions_router
from routes_ai_agent import init_ai_agent_routes
from routes_risk_dashboard import init_risk_dashboard_routes
from routes_market_intelligence import init_market_intelligence_routes
from routes_strategy_editor import init_strategy_editor_routes
from routes_user_system import init_user_system_routes
from routes_notification_system import init_notification_system_routes


def create_app() -> FastAPI:
    app = FastAPI(title='AI-Trader API')

    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    @app.middleware('http')
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        response.headers['X-Process-Time'] = str(time.time() - start_time)
        return response

    ctx = RouteContext()
    register_market_routes(app, ctx)
    register_agent_routes(app, ctx)
    register_signal_routes(app, ctx)
    register_trading_routes(app, ctx)
    register_experiment_routes(app, ctx)
    register_research_routes(app, ctx)
    register_challenge_routes(app, ctx)
    register_team_mission_routes(app, ctx)
    register_user_routes(app, ctx)
    
    app.include_router(extensions_router)
    
    init_ai_agent_routes(app)
    init_risk_dashboard_routes(app)
    init_market_intelligence_routes(app)
    init_strategy_editor_routes(app)
    init_user_system_routes(app)
    init_notification_system_routes(app)
    
    register_misc_routes(app)
    return app
