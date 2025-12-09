"""
Mock Vertex Search Service for testing without GCP credentials
"""
from typing import List
from src.models.schemas import Scheme

class MockVertexSearchService:
    """Mock search service that returns sample schemes"""
    
    def __init__(self, datastore_path: str):
        self.datastore_path = datastore_path
        self.is_farmer = "farmer" in datastore_path.lower()
        print(f"🔧 Mock mode: Using sample {'farmer' if self.is_farmer else 'MSME'} schemes")
    
    def search(self, query: str, top_k: int = 10) -> List[Scheme]:
        """Return mock schemes based on category"""
        print(f"🔍 Mock search: '{query}' (top {top_k})")
        
        if self.is_farmer:
            return self._get_mock_farmer_schemes()[:top_k]
        else:
            return self._get_mock_msme_schemes()[:top_k]
    
    def _get_mock_farmer_schemes(self) -> List[Scheme]:
        """Mock farmer schemes"""
        return [
            Scheme(
                id="farmer-1",
                name="PM-KISAN Scheme",
                description="Direct income support of ₹6000 per year to farmer families owning cultivable land",
                eligibility="All landholding farmer families across the country",
                benefits="Financial benefit of ₹6000 per year in three equal installments of ₹2000 each",
                application_process="Register online at pmkisan.gov.in portal or visit nearest Common Service Center",
                url="https://pmkisan.gov.in"
            ),
            Scheme(
                id="farmer-2",
                name="Kisan Credit Card (KCC)",
                description="Credit facility for farmers to meet short term credit requirements for cultivation and other needs",
                eligibility="Farmers - individual/joint borrowers who are owner cultivators, tenant farmers, oral lessees, and sharecroppers",
                benefits="Flexible credit limit, minimal documentation, low interest rates (4% per annum), insurance coverage",
                application_process="Apply through any commercial bank, RRB, cooperative bank with land ownership documents",
                url="https://pmkisan.gov.in/Rpo_FarmerCreditCard.aspx"
            ),
            Scheme(
                id="farmer-3",
                name="Pradhan Mantri Fasal Bima Yojana (PMFBY)",
                description="Comprehensive crop insurance scheme providing financial support to farmers in case of crop loss",
                eligibility="All farmers including sharecroppers and tenant farmers growing notified crops",
                benefits="Coverage for natural calamities, pests, and diseases. Premium: 2% for Kharif, 1.5% for Rabi crops",
                application_process="Apply within stipulated time through banks, insurance companies or online portal",
                url="https://pmfby.gov.in"
            ),
            Scheme(
                id="farmer-4",
                name="PM Kisan Samman Nidhi Yojana",
                description="Income support scheme for small and marginal farmers",
                eligibility="Small and marginal farmer families having combined land holding up to 2 hectares",
                benefits="₹6000 per year paid in three equal installments directly to bank accounts",
                application_process="Self-registration on PM-KISAN portal or through local revenue officer",
                url="https://pmkisan.gov.in"
            ),
            Scheme(
                id="farmer-5",
                name="Soil Health Card Scheme",
                description="Provides information on nutrient status of soil along with recommendations on dosage of nutrients",
                eligibility="All farmers across the country",
                benefits="Free soil testing, customized fertilizer recommendations, improved crop yield",
                application_process="Contact local agriculture department or soil testing laboratory",
                url="https://soilhealth.dac.gov.in"
            ),
            Scheme(
                id="farmer-6",
                name="Pradhan Mantri Krishi Sinchai Yojana",
                description="Irrigation scheme to expand cultivable area with assured irrigation",
                eligibility="All farmers engaged in agriculture",
                benefits="Financial assistance for drip/sprinkler irrigation, farm ponds, and other water conservation methods",
                application_process="Apply through state agriculture department",
                url="https://pmksy.gov.in"
            ),
            Scheme(
                id="farmer-7",
                name="National Agriculture Market (e-NAM)",
                description="Online trading platform for agricultural commodities",
                eligibility="All farmers and traders",
                benefits="Better price realization, reduced transaction costs, increased transparency",
                application_process="Register on e-NAM portal with required documents",
                url="https://enam.gov.in"
            ),
            Scheme(
                id="farmer-8",
                name="Kisan Call Centre",
                description="Telephone helpline for farmers to answer queries related to agriculture",
                eligibility="All farmers",
                benefits="Free advisory services in local languages on crop cultivation, pest management, prices",
                application_process="Call toll-free number 1800-180-1551",
                url="https://mkisan.gov.in"
            ),
            Scheme(
                id="farmer-9",
                name="Paramparagat Krishi Vikas Yojana",
                description="Organic farming support scheme",
                eligibility="Farmers interested in organic farming",
                benefits="Financial assistance of ₹50,000 per hectare over 3 years, certification support",
                application_process="Apply through state agriculture department",
                url="https://pgsindia-ncof.gov.in"
            ),
            Scheme(
                id="farmer-10",
                name="Rashtriya Krishi Vikas Yojana",
                description="State plan scheme for holistic development of agriculture",
                eligibility="State governments for benefiting farmers",
                benefits="Infrastructure development, value addition, market support",
                application_process="Implemented through state agriculture departments",
                url="https://rkvy.nic.in"
            ),
        ]
    
    def _get_mock_msme_schemes(self) -> List[Scheme]:
        """Mock MSME schemes"""
        return [
            Scheme(
                id="msme-1",
                name="Credit Guarantee Fund Trust for Micro and Small Enterprises (CGTMSE)",
                description="Collateral-free credit facility for micro and small enterprises",
                eligibility="New and existing micro and small enterprises in manufacturing and service sector",
                benefits="Loans up to ₹2 crore without collateral or third-party guarantee, reduced interest rates",
                application_process="Apply through CGTMSE member lending institutions (banks, NBFCs)",
                url="https://www.cgtmse.in"
            ),
            Scheme(
                id="msme-2",
                name="MUDRA Loan Scheme",
                description="Funding scheme for non-corporate, non-farm small/micro enterprises under three categories",
                eligibility="Non-corporate, non-farm income generating activities up to ₹10 lakh",
                benefits="Shishu (up to ₹50k), Kishore (₹50k-₹5L), Tarun (₹5L-₹10L) loans at competitive rates",
                application_process="Apply online or through any bank, NBFC, or MFI",
                url="https://www.mudra.org.in"
            ),
            Scheme(
                id="msme-3",
                name="Prime Minister's Employment Generation Programme (PMEGP)",
                description="Credit-linked subsidy scheme for setting up micro-enterprises",
                eligibility="Any individual above 18 years. Special category beneficiaries get higher subsidy",
                benefits="Subsidy: 15-35% for manufacturing, 15-25% for service sector. Max subsidy ₹25 lakh",
                application_process="Apply online at KVIC portal or through District Industries Centre",
                url="https://www.kviconline.gov.in/pmegp"
            ),
            Scheme(
                id="msme-4",
                name="Credit Linked Capital Subsidy Scheme (CLCSS)",
                description="Technology upgradation scheme for MSMEs",
                eligibility="Small Scale Industries (SSI) for technology upgradation",
                benefits="15% capital subsidy (maximum ₹15 lakh) on institutional finance of up to ₹1 crore",
                application_process="Apply through banks approved under the scheme",
                url="https://dcmsme.gov.in"
            ),
            Scheme(
                id="msme-5",
                name="Stand-Up India Scheme",
                description="Facilitating bank loans for SC/ST and women entrepreneurs",
                eligibility="SC/ST and/or Women entrepreneurs setting up greenfield enterprise",
                benefits="Loans between ₹10 lakh to ₹1 crore for non-farm sector activities",
                application_process="Apply through any scheduled commercial bank branch",
                url="https://www.standupmitra.in"
            ),
            Scheme(
                id="msme-6",
                name="Udyam Registration (formerly Udyog Aadhaar)",
                description="Online registration portal for MSMEs",
                eligibility="All micro, small, and medium enterprises",
                benefits="Free registration, access to various government schemes, priority sector lending status",
                application_process="Self-declaration based online registration with Aadhaar and PAN",
                url="https://udyamregistration.gov.in"
            ),
            Scheme(
                id="msme-7",
                name="Market Development Assistance (MDA) Scheme",
                description="Financial assistance for participation in trade fairs and exhibitions",
                eligibility="MSMEs and their associations/consortia",
                benefits="75% of space rental and airfare subsidy for international fairs",
                application_process="Apply through Office of Development Commissioner (MSME)",
                url="https://dcmsme.gov.in"
            ),
            Scheme(
                id="msme-8",
                name="Micro & Small Enterprises Cluster Development Programme (MSE-CDP)",
                description="Support for cluster-based development of MSMEs",
                eligibility="Cluster of at least 50 micro/small enterprises",
                benefits="Diagnostic study, capacity building, infrastructure development support up to ₹15 crore",
                application_process="Apply through state government or field office of MSME-DI",
                url="https://dcmsme.gov.in"
            ),
            Scheme(
                id="msme-9",
                name="ZED (Zero Defect Zero Effect) Certification",
                description="Quality certification scheme for MSMEs",
                eligibility="All MSMEs",
                benefits="80% subsidy on ZED certification cost (up to ₹80,000), improved competitiveness",
                application_process="Register on ZED portal and engage certified consultants",
                url="https://zed.msme.gov.in"
            ),
            Scheme(
                id="msme-10",
                name="Technology and Quality Upgradation Support (TEQUP)",
                description="Technology adoption and quality improvement support",
                eligibility="MSMEs in manufacturing sector",
                benefits="Technology upgradation, quality certification, testing facility access",
                application_process="Apply through Quality Council of India or MSME Technology Centers",
                url="https://qcin.org"
            ),
        ]