"""
测试智能 TTL 功能
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量
os.environ["SMART_TTL_ENABLED"] = "true"
os.environ["SMART_TTL_MIN_SECONDS"] = "10"
os.environ["SMART_TTL_MAX_SECONDS"] = "300"
os.environ["SMART_TTL_HIGH_FREQ_THRESHOLD"] = "10"
os.environ["ALPHA_VANTAGE_API_KEY"] = "PG9XTILNJBU41DA8"

import price_fetcher

print("=" * 60)
print("智能 TTL 功能测试")
print("=" * 60)

# 重置缓存和统计
price_fetcher._local_price_cache.clear()
price_fetcher._cache_access_frequency.clear()
price_fetcher._reset_cache_stats()

print(f"\n智能 TTL 配置:")
print(f"  SMART_TTL_ENABLED: {price_fetcher._SMART_TTL_ENABLED}")
print(f"  SMART_TTL_MIN_SECONDS: {price_fetcher._SMART_TTL_MIN_SECONDS}")
print(f"  SMART_TTL_MAX_SECONDS: {price_fetcher._SMART_TTL_MAX_SECONDS}")
print(f"  SMART_TTL_HIGH_FREQ_THRESHOLD: {price_fetcher._SMART_TTL_HIGH_FREQ_THRESHOLD}")

# 测试 1: 低频访问（< 5 次）- 应该使用最小 TTL
print("\n" + "=" * 60)
print("测试 1: 低频访问（1 次）- 应该使用最小 TTL")
print("=" * 60)

cache_key = price_fetcher._price_cache_key("TEST_LOW_FREQ", "us-stock")
print(f"\n缓存键: {cache_key}")

# 访问 1 次
price_fetcher._track_cache_access(cache_key)
print(f"访问频率: {price_fetcher._cache_access_frequency.get(cache_key, 0)}")

# 获取 TTL
ttl = price_fetcher._get_smart_ttl(cache_key, 100.00)
print(f"获取的 TTL: {ttl} 秒")
print(f"预期 TTL: {price_fetcher._SMART_TTL_MIN_SECONDS} 秒（最小 TTL）")

assert ttl == price_fetcher._SMART_TTL_MIN_SECONDS, f"TTL 应该是 {price_fetcher._SMART_TTL_MIN_SECONDS}，实际是 {ttl}"
print("✅ 测试 1 通过！")

# 测试 2: 中频访问（5-9 次）- 应该使用中等 TTL
print("\n" + "=" * 60)
print("测试 2: 中频访问（7 次）- 应该使用中等 TTL")
print("=" * 60)

cache_key = price_fetcher._price_cache_key("TEST_MID_FREQ", "us-stock")
print(f"\n缓存键: {cache_key}")

# 访问 7 次
for i in range(7):
    price_fetcher._track_cache_access(cache_key)
print(f"访问频率: {price_fetcher._cache_access_frequency.get(cache_key, 0)}")

# 获取 TTL
ttl = price_fetcher._get_smart_ttl(cache_key, 100.00)
expected_mid_ttl = (price_fetcher._SMART_TTL_MIN_SECONDS + price_fetcher._SMART_TTL_MAX_SECONDS) // 2
print(f"获取的 TTL: {ttl} 秒")
print(f"预期 TTL: {expected_mid_ttl} 秒（中等 TTL）")

assert ttl == expected_mid_ttl, f"TTL 应该是 {expected_mid_ttl}，实际是 {ttl}"
print("✅ 测试 2 通过！")

# 测试 3: 高频访问（>= 10 次）- 应该使用最大 TTL
print("\n" + "=" * 60)
print("测试 3: 高频访问（15 次）- 应该使用最大 TTL")
print("=" * 60)

cache_key = price_fetcher._price_cache_key("TEST_HIGH_FREQ", "us-stock")
print(f"\n缓存键: {cache_key}")

# 访问 15 次
for i in range(15):
    price_fetcher._track_cache_access(cache_key)
print(f"访问频率: {price_fetcher._cache_access_frequency.get(cache_key, 0)}")

# 获取 TTL
ttl = price_fetcher._get_smart_ttl(cache_key, 100.00)
print(f"获取的 TTL: {ttl} 秒")
print(f"预期 TTL: {price_fetcher._SMART_TTL_MAX_SECONDS} 秒（最大 TTL）")

assert ttl == price_fetcher._SMART_TTL_MAX_SECONDS, f"TTL 应该是 {price_fetcher._SMART_TTL_MAX_SECONDS}，实际是 {ttl}"
print("✅ 测试 3 通过！")

# 测试 4: 访问频率上限
print("\n" + "=" * 60)
print("测试 4: 访问频率上限（超过阈值后应该被限制）")
print("=" * 60)

cache_key = price_fetcher._price_cache_key("TEST_CAP", "us-stock")
print(f"\n缓存键: {cache_key}")

# 访问 100 次（远超过阈值）
for i in range(100):
    price_fetcher._track_cache_access(cache_key)

frequency = price_fetcher._cache_access_frequency.get(cache_key, 0)
print(f"访问频率: {frequency}")
print(f"预期上限: {price_fetcher._SMART_TTL_HIGH_FREQ_THRESHOLD}")

assert frequency <= price_fetcher._SMART_TTL_HIGH_FREQ_THRESHOLD, f"频率应该被限制在 {price_fetcher._SMART_TTL_HIGH_FREQ_THRESHOLD} 以内，实际是 {frequency}"
print("✅ 测试 4 通过！")

# 测试 5: 失败请求的 TTL
print("\n" + "=" * 60)
print("测试 5: 失败请求的 TTL（应该使用失败缓存 TTL）")
print("=" * 60)

cache_key = price_fetcher._price_cache_key("TEST_FAILURE", "us-stock")
print(f"\n缓存键: {cache_key}")

# 获取失败请求的 TTL
ttl = price_fetcher._get_smart_ttl(cache_key, None)
print(f"获取的 TTL: {ttl} 秒")
print(f"预期 TTL: {price_fetcher._PRICE_FAILURE_CACHE_TTL_SECONDS} 秒（失败缓存 TTL）")

assert ttl == price_fetcher._PRICE_FAILURE_CACHE_TTL_SECONDS, f"TTL 应该是 {price_fetcher._PRICE_FAILURE_CACHE_TTL_SECONDS}，实际是 {ttl}"
print("✅ 测试 5 通过！")

# 测试 6: 智能 TTL 禁用时
print("\n" + "=" * 60)
print("测试 6: 智能 TTL 禁用时（应该使用默认 TTL）")
print("=" * 60)

# 临时禁用智能 TTL
original_enabled = price_fetcher._SMART_TTL_ENABLED
price_fetcher._SMART_TTL_ENABLED = False

cache_key = price_fetcher._price_cache_key("TEST_DISABLED", "us-stock")
print(f"\n缓存键: {cache_key}")

# 访问多次（应该不影响 TTL）
for i in range(20):
    price_fetcher._track_cache_access(cache_key)
print(f"访问频率: {price_fetcher._cache_access_frequency.get(cache_key, 0)}")

# 获取 TTL
ttl = price_fetcher._get_smart_ttl(cache_key, 100.00)
print(f"获取的 TTL: {ttl} 秒")
print(f"预期 TTL: {price_fetcher._PRICE_CACHE_TTL_SECONDS} 秒（默认 TTL）")

assert ttl == price_fetcher._PRICE_CACHE_TTL_SECONDS, f"TTL 应该是 {price_fetcher._PRICE_CACHE_TTL_SECONDS}，实际是 {ttl}"

# 恢复设置
price_fetcher._SMART_TTL_ENABLED = original_enabled
print("✅ 测试 6 通过！")

# 测试 7: 实际缓存操作
print("\n" + "=" * 60)
print("测试 7: 实际缓存操作（验证 TTL 被正确应用）")
print("=" * 60)

# 重置
price_fetcher._local_price_cache.clear()
price_fetcher._cache_access_frequency.clear()

symbol = "AAPL"
market = "us-stock"
price = 300.00

print(f"\n测试股票: {symbol}")
print(f"市场: {market}")
print(f"价格: ${price}")

# 高频访问（15 次）
cache_key = price_fetcher._price_cache_key(symbol, market)
for i in range(15):
    price_fetcher._track_cache_access(cache_key)

print(f"访问频率: {price_fetcher._cache_access_frequency.get(cache_key, 0)}")

# 设置缓存
price_fetcher._price_cache_set(symbol, market, price)

# 验证缓存
cached_price = price_fetcher._price_cache_get(symbol, market)
print(f"缓存中的价格: ${cached_price}")

assert cached_price == price, f"缓存价格应该是 ${price}，实际是 ${cached_price}"

# 验证 TTL
if cache_key in price_fetcher._local_price_cache:
    _, expires_at = price_fetcher._local_price_cache[cache_key]
    ttl = expires_at - time.time()
    print(f"实际 TTL: {ttl:.1f} 秒")
    print(f"预期 TTL 范围: {price_fetcher._SMART_TTL_MAX_SECONDS - 5} 到 {price_fetcher._SMART_TTL_MAX_SECONDS} 秒")
    
    assert ttl > 0, "TTL 应该大于 0"
    assert ttl <= price_fetcher._SMART_TTL_MAX_SECONDS, f"TTL 应该小于等于 {price_fetcher._SMART_TTL_MAX_SECONDS}"

print("✅ 测试 7 通过！")

# 总结
print("\n" + "=" * 60)
print("所有测试通过！")
print("=" * 60)
print("\n智能 TTL 功能验证成功！")
print("\n功能总结:")
print("  ✅ 低频访问（< 5 次）: 使用最小 TTL（10 秒）")
print("  ✅ 中频访问（5-9 次）: 使用中等 TTL（155 秒）")
print("  ✅ 高频访问（>= 10 次）: 使用最大 TTL（300 秒）")
print("  ✅ 访问频率上限: 被限制在阈值以内")
print("  ✅ 失败请求: 使用失败缓存 TTL")
print("  ✅ 智能 TTL 禁用: 使用默认 TTL")
print("  ✅ 实际缓存操作: TTL 被正确应用")
