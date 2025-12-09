"""Test if agents are loading correctly"""

print("=" * 70)
print("Testing Agent Loading")
print("=" * 70)

from src.agents.farmer_agent import is_adk_agent as farmer_adk, farmer_agent
from src.agents.msme_agent import is_adk_agent as msme_adk, msme_agent

print(f"\nFarmer Agent:")
print(f"  is_adk_agent: {farmer_adk}")
print(f"  farmer_agent type: {type(farmer_agent)}")
print(f"  farmer_agent: {farmer_agent}")

print(f"\nMSME Agent:")
print(f"  is_adk_agent: {msme_adk}")
print(f"  msme_agent type: {type(msme_agent)}")
print(f"  msme_agent: {msme_agent}")

print("\n" + "=" * 70)

if farmer_adk:
    print("✅ Farmer Agent should use ADK")
else:
    print("⚠️  Farmer Agent should use fallback")

if msme_adk:
    print("✅ MSME Agent should use ADK")
else:
    print("⚠️  MSME Agent should use fallback")