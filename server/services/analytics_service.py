from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from sqlalchemy import func, and_, or_, desc, case
from collections import defaultdict

from database import get_db
from models import User, Signal, Trade, Order, Position, AnalyticsEvent, ABTest, Notification
from middleware.error_handler import success_response, error_response


def track_event(user_id: Optional[int], event_type: str, event_name: str, 
                properties: Optional[Dict] = None, session_id: Optional[str] = None) -> None:
    db = next(get_db())
    try:
        event = AnalyticsEvent(
            user_id=user_id,
            event_type=event_type,
            event_name=event_name,
            properties=properties or {},
            session_id=session_id
        )
        db.add(event)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[Analytics] Failed to track event: {e}")
    finally:
        db.close()


def get_user_analytics(user_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
    start_date = params.get('start_date')
    end_date = params.get('end_date')
    days = int(params.get('days', 30))

    db = next(get_db())
    try:
        end_dt = datetime.now(timezone.utc)
        start_dt = end_dt - timedelta(days=days)
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
        if end_date:
            end_dt = datetime.fromisoformat(end_date)

        trades = db.query(Trade).filter(
            Trade.user_id == user_id,
            Trade.is_simulation == True,
            Trade.created_at >= start_dt,
            Trade.created_at <= end_dt
        ).all()

        signals = db.query(Signal).filter(
            Signal.user_id == user_id,
            Signal.created_at >= start_dt,
            Signal.created_at <= end_dt
        ).all()

        events = db.query(AnalyticsEvent).filter(
            AnalyticsEvent.user_id == user_id,
            AnalyticsEvent.created_at >= start_dt,
            AnalyticsEvent.created_at <= end_dt
        ).all()

        daily_stats = _calculate_daily_stats(trades, start_dt, end_dt)
        performance_metrics = _calculate_performance_metrics(trades)
        behavior_metrics = _calculate_behavior_metrics(events, signals, trades)

        return success_response({
            'period': {
                'start_date': start_dt.isoformat(),
                'end_date': end_dt.isoformat(),
                'days': days
            },
            'daily_stats': daily_stats,
            'performance': performance_metrics,
            'behavior': behavior_metrics
        })

    except Exception as e:
        return error_response(f'获取用户分析数据失败: {str(e)}', 500)
    finally:
        db.close()


def _calculate_daily_stats(trades: List[Trade], start_dt: datetime, end_dt: datetime) -> List[Dict[str, Any]]:
    daily_data = defaultdict(lambda: {'trades': 0, 'pnl': 0, 'volume': 0})
    
    for trade in trades:
        if trade.created_at:
            day = trade.created_at.date().isoformat()
            daily_data[day]['trades'] += 1
            daily_data[day]['pnl'] += trade.pnl or 0
            daily_data[day]['volume'] += (trade.quantity or 0) * (trade.price or 0)

    result = []
    current = start_dt.date()
    end = end_dt.date()
    
    while current <= end:
        day_str = current.isoformat()
        data = daily_data.get(day_str, {'trades': 0, 'pnl': 0, 'volume': 0})
        result.append({
            'date': day_str,
            'trades': data['trades'],
            'pnl': round(data['pnl'], 2),
            'volume': round(data['volume'], 2)
        })
        current += timedelta(days=1)

    return result


def _calculate_performance_metrics(trades: List[Trade]) -> Dict[str, Any]:
    if not trades:
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'total_pnl': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'profit_factor': 0,
            'best_trade': 0,
            'worst_trade': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0
        }

    winning_trades = [t for t in trades if t.pnl and t.pnl > 0]
    losing_trades = [t for t in trades if t.pnl and t.pnl < 0]
    
    total_pnl = sum(t.pnl or 0 for t in trades)
    avg_win = sum(t.pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0
    avg_loss = sum(t.pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0
    profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
    
    best_trade = max((t.pnl for t in trades if t.pnl), default=0)
    worst_trade = min((t.pnl for t in trades if t.pnl), default=0)
    
    win_rate = len(winning_trades) / len(trades) * 100

    pnl_values = [t.pnl or 0 for t in trades]
    if len(pnl_values) > 1:
        import statistics
        mean = sum(pnl_values) / len(pnl_values)
        std = statistics.stdev(pnl_values) if len(pnl_values) > 1 else 1
        sharpe_ratio = (mean / std) * (365 ** 0.5) if std != 0 else 0
    else:
        sharpe_ratio = 0

    cumulative = []
    current = 0
    peak = 0
    max_drawdown = 0
    for pnl in pnl_values:
        current += pnl
        if current > peak:
            peak = current
        drawdown = (peak - current) / peak * 100 if peak > 0 else 0
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    return {
        'total_trades': len(trades),
        'winning_trades': len(winning_trades),
        'losing_trades': len(losing_trades),
        'win_rate': round(win_rate, 2),
        'total_pnl': round(total_pnl, 2),
        'avg_win': round(avg_win, 2),
        'avg_loss': round(avg_loss, 2),
        'profit_factor': round(profit_factor, 2),
        'best_trade': round(best_trade, 2),
        'worst_trade': round(worst_trade, 2),
        'sharpe_ratio': round(sharpe_ratio, 2),
        'max_drawdown': round(max_drawdown, 2)
    }


def _calculate_behavior_metrics(events: List[AnalyticsEvent], signals: List[Signal], trades: List[Trade]) -> Dict[str, Any]:
    event_types = defaultdict(int)
    for event in events:
        event_types[event.event_type] += 1

    avg_time_between_trades = 0
    if len(trades) > 1:
        sorted_trades = sorted(trades, key=lambda t: t.created_at or datetime.min)
        intervals = []
        for i in range(1, len(sorted_trades)):
            if sorted_trades[i].created_at and sorted_trades[i-1].created_at:
                diff = (sorted_trades[i].created_at - sorted_trades[i-1].created_at).total_seconds()
                intervals.append(diff)
        if intervals:
            avg_time_between_trades = sum(intervals) / len(intervals)

    symbols_traded = set(t.symbol for t in trades)
    most_traded_symbol = None
    if symbols_traded:
        symbol_counts = defaultdict(int)
        for t in trades:
            symbol_counts[t.symbol] += 1
        most_traded_symbol = max(symbol_counts.items(), key=lambda x: x[1])[0]

    return {
        'total_events': len(events),
        'events_by_type': dict(event_types),
        'signals_created': len(signals),
        'avg_time_between_trades_seconds': round(avg_time_between_trades, 2),
        'symbols_traded': list(symbols_traded),
        'most_traded_symbol': most_traded_symbol,
        'session_count': len(set(e.session_id for e in events if e.session_id))
    }


def get_platform_analytics(params: Dict[str, Any]) -> Dict[str, Any]:
    days = int(params.get('days', 30))

    db = next(get_db())
    try:
        end_dt = datetime.now(timezone.utc)
        start_dt = end_dt - timedelta(days=days)

        total_users = db.query(User).count()
        active_users = db.query(User).filter(
            User.last_login_at >= start_dt
        ).count()
        new_users = db.query(User).filter(
            User.created_at >= start_dt
        ).count()

        total_signals = db.query(Signal).count()
        active_signals = db.query(Signal).filter(Signal.status == 'active').count()
        new_signals = db.query(Signal).filter(
            Signal.created_at >= start_dt
        ).count()

        total_trades = db.query(Trade).count()
        new_trades = db.query(Trade).filter(
            Trade.created_at >= start_dt
        ).count()
        total_volume = db.query(func.sum(Trade.quantity * Trade.price)).filter(
            Trade.created_at >= start_dt
        ).scalar() or 0

        total_pnl = db.query(func.sum(Trade.pnl)).filter(
            Trade.created_at >= start_dt
        ).scalar() or 0

        top_traders = db.query(
            User.id,
            User.username,
            User.display_name,
            func.sum(Trade.pnl).label('total_pnl')
        ).join(Trade).filter(
            Trade.created_at >= start_dt,
            Trade.is_simulation == True
        ).group_by(User.id).order_by(desc('total_pnl')).limit(10).all()

        top_signals = db.query(
            Signal.id,
            Signal.title,
            Signal.symbols,
            Signal.pnl,
            Signal.pnl_percent,
            User.username,
            User.display_name
        ).join(User).filter(
            Signal.created_at >= start_dt
        ).order_by(desc(Signal.pnl)).limit(10).all()

        return success_response({
            'period': {'days': days},
            'users': {
                'total': total_users,
                'active': active_users,
                'new': new_users,
                'growth_rate': round((new_users / total_users * 100) if total_users > 0 else 0, 2)
            },
            'signals': {
                'total': total_signals,
                'active': active_signals,
                'new': new_signals
            },
            'trading': {
                'total_trades': total_trades,
                'new_trades': new_trades,
                'total_volume': round(total_volume, 2),
                'total_pnl': round(total_pnl, 2)
            },
            'leaderboards': {
                'top_traders': [{
                    'id': t[0],
                    'username': t[1],
                    'display_name': t[2],
                    'total_pnl': round(t[3] or 0, 2)
                } for t in top_traders],
                'top_signals': [{
                    'id': s[0],
                    'title': s[1],
                    'symbols': s[2],
                    'pnl': round(s[3] or 0, 2),
                    'pnl_percent': round(s[4] or 0, 2),
                    'author_username': s[5],
                    'author_display_name': s[6]
                } for s in top_signals]
            }
        })

    except Exception as e:
        return error_response(f'获取平台分析数据失败: {str(e)}', 500)
    finally:
        db.close()


def create_ab_test(admin_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    name = data.get('name')
    feature_name = data.get('feature_name')
    variants = data.get('variants', [])
    traffic_split = data.get('traffic_split', {})

    if not name or not feature_name or not variants:
        return error_response('缺少必要参数', 400)

    db = next(get_db())
    try:
        existing = db.query(ABTest).filter(ABTest.name == name).first()
        if existing:
            return error_response('测试名称已存在', 400)

        ab_test = ABTest(
            name=name,
            feature_name=feature_name,
            variants=variants,
            traffic_split=traffic_split,
            is_active=False
        )

        db.add(ab_test)
        db.commit()
        db.refresh(ab_test)

        return success_response(_ab_test_to_dict(ab_test))

    except Exception as e:
        db.rollback()
        return error_response(f'创建A/B测试失败: {str(e)}', 500)
    finally:
        db.close()


def get_ab_tests(params: Dict[str, Any]) -> Dict[str, Any]:
    is_active = params.get('is_active')
    page = int(params.get('page', 1))
    per_page = int(params.get('per_page', 20))

    db = next(get_db())
    try:
        query = db.query(ABTest)
        
        if is_active is not None:
            query = query.filter(ABTest.is_active == is_active)

        total = query.count()
        tests = query.order_by(desc(ABTest.created_at)).offset((page - 1) * per_page).limit(per_page).all()

        return success_response({
            'items': [_ab_test_to_dict(t) for t in tests],
            'total': total,
            'page': page,
            'per_page': per_page
        })

    except Exception as e:
        return error_response(f'获取A/B测试列表失败: {str(e)}', 500)
    finally:
        db.close()


def get_user_ab_variant(user_id: int, feature_name: str) -> Dict[str, Any]:
    db = next(get_db())
    try:
        ab_test = db.query(ABTest).filter(
            ABTest.feature_name == feature_name,
            ABTest.is_active == True
        ).first()

        if not ab_test:
            return success_response({'variant': 'control', 'test_id': None})

        hash_value = hash(f"{user_id}:{ab_test.id}") % 100
        cumulative = 0
        assigned_variant = 'control'

        for variant, weight in ab_test.traffic_split.items():
            cumulative += weight
            if hash_value < cumulative:
                assigned_variant = variant
                break

        return success_response({
            'variant': assigned_variant,
            'test_id': ab_test.id,
            'test_name': ab_test.name
        })

    except Exception as e:
        return error_response(f'获取A/B测试变体失败: {str(e)}', 500)
    finally:
        db.close()


def track_ab_conversion(test_id: int, user_id: int, variant: str, conversion_type: str) -> Dict[str, Any]:
    db = next(get_db())
    try:
        ab_test = db.query(ABTest).filter(ABTest.id == test_id).first()
        if not ab_test:
            return error_response('A/B测试不存在', 404)

        results = ab_test.results or {}
        if variant not in results:
            results[variant] = {'views': 0, 'conversions': {}}
        
        if conversion_type not in results[variant]['conversions']:
            results[variant]['conversions'][conversion_type] = 0
        
        results[variant]['conversions'][conversion_type] += 1
        ab_test.results = results
        db.commit()

        return success_response({'message': '转化已记录'})

    except Exception as e:
        db.rollback()
        return error_response(f'记录转化失败: {str(e)}', 500)
    finally:
        db.close()


def _ab_test_to_dict(ab_test: ABTest) -> Dict[str, Any]:
    return {
        'id': ab_test.id,
        'name': ab_test.name,
        'feature_name': ab_test.feature_name,
        'variants': ab_test.variants,
        'traffic_split': ab_test.traffic_split,
        'is_active': ab_test.is_active,
        'results': ab_test.results,
        'created_at': ab_test.created_at.isoformat() if ab_test.created_at else None,
        'started_at': ab_test.started_at.isoformat() if ab_test.started_at else None,
        'ended_at': ab_test.ended_at.isoformat() if ab_test.ended_at else None
    }


def get_funnel_analysis(params: Dict[str, Any]) -> Dict[str, Any]:
    funnel_name = params.get('funnel', 'registration')
    days = int(params.get('days', 30))

    db = next(get_db())
    try:
        end_dt = datetime.now(timezone.utc)
        start_dt = end_dt - timedelta(days=days)

        if funnel_name == 'registration':
            total_visitors = db.query(func.count(func.distinct(AnalyticsEvent.session_id))).filter(
                AnalyticsEvent.event_type == 'page_view',
                AnalyticsEvent.created_at >= start_dt
            ).scalar() or 0

            signups = db.query(User).filter(
                User.created_at >= start_dt
            ).count()

            first_signal = db.query(func.count(func.distinct(Signal.user_id))).filter(
                Signal.created_at >= start_dt
            ).scalar() or 0

            first_trade = db.query(func.count(func.distinct(Trade.user_id))).filter(
                Trade.created_at >= start_dt
            ).scalar() or 0

            steps = [
                {'name': '访问者', 'count': total_visitors, 'conversion': 100},
                {'name': '注册用户', 'count': signups, 'conversion': round(signups / total_visitors * 100 if total_visitors > 0 else 0, 2)},
                {'name': '发布信号', 'count': first_signal, 'conversion': round(first_signal / signups * 100 if signups > 0 else 0, 2)},
                {'name': '完成交易', 'count': first_trade, 'conversion': round(first_trade / first_signal * 100 if first_signal > 0 else 0, 2)}
            ]

        elif funnel_name == 'trading':
            viewed_signals = db.query(func.count(func.distinct(AnalyticsEvent.user_id))).filter(
                AnalyticsEvent.event_name == 'view_signal',
                AnalyticsEvent.created_at >= start_dt
            ).scalar() or 0

            followed_signals = db.query(func.count(func.distinct(AnalyticsEvent.user_id))).filter(
                AnalyticsEvent.event_name == 'follow_signal',
                AnalyticsEvent.created_at >= start_dt
            ).scalar() or 0

            created_orders = db.query(func.count(func.distinct(Order.user_id))).filter(
                Order.created_at >= start_dt
            ).scalar() or 0

            completed_trades = db.query(func.count(func.distinct(Trade.user_id))).filter(
                Trade.created_at >= start_dt
            ).scalar() or 0

            steps = [
                {'name': '查看信号', 'count': viewed_signals, 'conversion': 100},
                {'name': '关注信号', 'count': followed_signals, 'conversion': round(followed_signals / viewed_signals * 100 if viewed_signals > 0 else 0, 2)},
                {'name': '创建订单', 'count': created_orders, 'conversion': round(created_orders / followed_signals * 100 if followed_signals > 0 else 0, 2)},
                {'name': '完成交易', 'count': completed_trades, 'conversion': round(completed_trades / created_orders * 100 if created_orders > 0 else 0, 2)}
            ]

        else:
            return error_response('不支持的漏斗类型', 400)

        return success_response({
            'funnel': funnel_name,
            'period': {'days': days},
            'steps': steps
        })

    except Exception as e:
        return error_response(f'获取漏斗分析失败: {str(e)}', 500)
    finally:
        db.close()


def get_retention_analysis(params: Dict[str, Any]) -> Dict[str, Any]:
    days = int(params.get('days', 30))
    cohort_days = int(params.get('cohort_days', 7))

    db = next(get_db())
    try:
        end_dt = datetime.now(timezone.utc)
        start_dt = end_dt - timedelta(days=days)

        cohorts = []
        
        for i in range(0, days, cohort_days):
            cohort_start = start_dt + timedelta(days=i)
            cohort_end = cohort_start + timedelta(days=cohort_days)
            
            cohort_users = db.query(User).filter(
                User.created_at >= cohort_start,
                User.created_at < cohort_end
            ).all()
            
            cohort_size = len(cohort_users)
            if cohort_size == 0:
                continue

            retention = []
            for week in range(0, 4):
                week_start = cohort_end + timedelta(days=week * 7)
                week_end = week_start + timedelta(days=7)
                
                active_users = db.query(func.count(func.distinct(AnalyticsEvent.user_id))).filter(
                    AnalyticsEvent.user_id.in_([u.id for u in cohort_users]),
                    AnalyticsEvent.created_at >= week_start,
                    AnalyticsEvent.created_at < week_end
                ).scalar() or 0
                
                retention.append({
                    'week': week + 1,
                    'active_users': active_users,
                    'rate': round(active_users / cohort_size * 100, 2)
                })

            cohorts.append({
                'cohort': cohort_start.date().isoformat(),
                'size': cohort_size,
                'retention': retention
            })

        return success_response({
            'period': {'days': days},
            'cohorts': cohorts
        })

    except Exception as e:
        return error_response(f'获取留存分析失败: {str(e)}', 500)
    finally:
        db.close()
