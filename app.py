import json
import uuid

import pandas as pd
import streamlit as st
from streamlit_local_storage import LocalStorage

# --------------------------------------------------------------------------
# 기본 설정
# --------------------------------------------------------------------------
st.set_page_config(page_title="대체원료 파인더", page_icon="🧪", layout="centered")

STORAGE_KEY = "substituteFinderIngredients_v1"

st.markdown(
    """
    <style>
    .tag {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 12px;
        margin: 2px 4px 2px 0;
        background: #e0e0e0;
        color: #444;
    }
    .tag.match { background: #4fb3a9; color: #fff; font-weight: 600; }
    .badge {
        display: inline-block;
        padding: 3px 9px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 700;
    }
    .badge.full { background: #dff5ea; color: #1c8a52; }
    .badge.partial { background: #fff4e0; color: #b8720b; }
    .selected-box {
        margin-top: 10px;
        padding: 14px 16px;
        border-radius: 12px;
        background: #f1f8f7;
        border: 1px dashed #a9d6cf;
    }
    .selected-box .name { font-weight: 700; font-size: 18px; }
    .selected-box .inci { color: #78909c; font-size: 13px; margin-bottom: 8px; }
    .result-table { width: 100%; border-collapse: collapse; font-size: 14px; }
    .result-table th, .result-table td {
        text-align: left; padding: 10px 8px; border-bottom: 1px solid #eceff1; vertical-align: top;
    }
    .result-table th { color: #607d8b; font-size: 12px; font-weight: 600; }
    .count { font-weight: 700; color: #4fb3a9; }
    </style>
    """,
    unsafe_allow_html=True,
)

DEFAULT_INGREDIENTS = [
  {
    "name": "잔탄검",
    "inci": "Xanthan Gum",
    "functions": [
      "점증"
    ]
  },
  {
    "name": "카보머",
    "inci": "Carbomer",
    "functions": [
      "점증"
    ]
  },
  {
    "name": "하이드록시에틸셀룰로오스",
    "inci": "Hydroxyethylcellulose",
    "functions": [
      "점증"
    ]
  },
  {
    "name": "아크릴레이트/C10-30 알킬아크릴레이트 크로스폴리머",
    "inci": "Acrylates/C10-30 Alkyl Acrylate Crosspolymer",
    "functions": [
      "점증"
    ]
  },
  {
    "name": "소듐폴리아크릴레이트",
    "inci": "Sodium Polyacrylate",
    "functions": [
      "점증",
      "보습"
    ]
  },
  {
    "name": "세테아릴알코올",
    "inci": "Cetearyl Alcohol",
    "functions": [
      "점증",
      "유화보조",
      "컨디셔닝"
    ]
  },
  {
    "name": "스테아린산",
    "inci": "Stearic Acid",
    "functions": [
      "점증",
      "유화보조"
    ]
  },
  {
    "name": "카라기난",
    "inci": "Carrageenan",
    "functions": [
      "점증"
    ]
  },
  {
    "name": "세테아레스-20",
    "inci": "Ceteareth-20",
    "functions": [
      "유화"
    ]
  },
  {
    "name": "폴리솔베이트60",
    "inci": "Polysorbate 60",
    "functions": [
      "유화",
      "가용화"
    ]
  },
  {
    "name": "글리세릴스테아레이트",
    "inci": "Glyceryl Stearate",
    "functions": [
      "유화",
      "컨디셔닝"
    ]
  },
  {
    "name": "소르비탄올리에이트",
    "inci": "Sorbitan Oleate",
    "functions": [
      "유화"
    ]
  },
  {
    "name": "레시틴",
    "inci": "Lecithin",
    "functions": [
      "유화",
      "컨디셔닝"
    ]
  },
  {
    "name": "PEG-100 스테아레이트",
    "inci": "PEG-100 Stearate",
    "functions": [
      "유화"
    ]
  },
  {
    "name": "세테아릴글루코사이드",
    "inci": "Cetearyl Glucoside",
    "functions": [
      "유화",
      "컨디셔닝"
    ]
  },
  {
    "name": "글리세린",
    "inci": "Glycerin",
    "functions": [
      "보습"
    ]
  },
  {
    "name": "부틸렌글라이콜",
    "inci": "Butylene Glycol",
    "functions": [
      "보습",
      "용제"
    ]
  },
  {
    "name": "프로판다이올",
    "inci": "Propanediol",
    "functions": [
      "보습",
      "용제"
    ]
  },
  {
    "name": "히알루론산나트륨",
    "inci": "Sodium Hyaluronate",
    "functions": [
      "보습"
    ]
  },
  {
    "name": "소르비톨",
    "inci": "Sorbitol",
    "functions": [
      "보습"
    ]
  },
  {
    "name": "판테놀",
    "inci": "Panthenol",
    "functions": [
      "보습",
      "컨디셔닝"
    ]
  },
  {
    "name": "베타인",
    "inci": "Betaine",
    "functions": [
      "보습",
      "컨디셔닝"
    ]
  },
  {
    "name": "우레아",
    "inci": "Urea",
    "functions": [
      "보습"
    ]
  },
  {
    "name": "호호바오일",
    "inci": "Jojoba Oil",
    "functions": [
      "에몰리언트",
      "컨디셔닝"
    ]
  },
  {
    "name": "스쿠알란",
    "inci": "Squalane",
    "functions": [
      "에몰리언트",
      "보습"
    ]
  },
  {
    "name": "카프릴릭/카프릭트라이글리세라이드",
    "inci": "Caprylic/Capric Triglyceride",
    "functions": [
      "에몰리언트"
    ]
  },
  {
    "name": "다이메티콘",
    "inci": "Dimethicone",
    "functions": [
      "에몰리언트",
      "컨디셔닝"
    ]
  },
  {
    "name": "시어버터",
    "inci": "Shea Butter",
    "functions": [
      "에몰리언트",
      "보습"
    ]
  },
  {
    "name": "소듐라우레스설페이트",
    "inci": "Sodium Laureth Sulfate",
    "functions": [
      "계면활성"
    ]
  },
  {
    "name": "코카미도프로필베타인",
    "inci": "Cocamidopropyl Betaine",
    "functions": [
      "계면활성",
      "컨디셔닝"
    ]
  },
  {
    "name": "데실글루코사이드",
    "inci": "Decyl Glucoside",
    "functions": [
      "계면활성"
    ]
  },
  {
    "name": "페녹시에탄올",
    "inci": "Phenoxyethanol",
    "functions": [
      "방부"
    ]
  },
  {
    "name": "에칠헥실글리세린",
    "inci": "Ethylhexylglycerin",
    "functions": [
      "방부보조",
      "컨디셔닝"
    ]
  },
  {
    "name": "1,2-헥산다이올",
    "inci": "1,2-Hexanediol",
    "functions": [
      "방부보조",
      "보습"
    ]
  },
  {
    "name": "시트르산",
    "inci": "Citric Acid",
    "functions": [
      "pH조절"
    ]
  },
  {
    "name": "수산화나트륨",
    "inci": "Sodium Hydroxide",
    "functions": [
      "pH조절"
    ]
  },
  {
    "name": "토코페롤",
    "inci": "Tocopherol",
    "functions": [
      "항산화",
      "컨디셔닝"
    ]
  },
  {
    "name": "BHT",
    "inci": "BHT",
    "functions": [
      "항산화"
    ]
  },
  {
    "name": "PEG-40 하이드로제네이티드캐스터오일",
    "inci": "PEG-40 Hydrogenated Castor Oil",
    "functions": [
      "가용화"
    ]
  },
  {
    "name": "폴리솔베이트20",
    "inci": "Polysorbate 20",
    "functions": [
      "가용화",
      "유화"
    ]
  },
  {
    "name": "하이드록시프로필메틸셀룰로오스",
    "inci": "Hydroxypropyl Methylcellulose",
    "functions": [
      "점증"
    ]
  },
  {
    "name": "구아검",
    "inci": "Guar Gum",
    "functions": [
      "점증"
    ]
  },
  {
    "name": "하이드록시프로필구아",
    "inci": "Hydroxypropyl Guar",
    "functions": [
      "점증"
    ]
  },
  {
    "name": "소듐카복시메틸셀룰로오스",
    "inci": "Sodium Carboxymethyl Cellulose",
    "functions": [
      "점증"
    ]
  },
  {
    "name": "아라비아검",
    "inci": "Acacia Senegal Gum",
    "functions": [
      "점증",
      "피막형성"
    ]
  },
  {
    "name": "젤란검",
    "inci": "Gellan Gum",
    "functions": [
      "점증"
    ]
  },
  {
    "name": "벤토나이트",
    "inci": "Bentonite",
    "functions": [
      "점증",
      "흡착"
    ]
  },
  {
    "name": "하이드레이티드실리카",
    "inci": "Hydrated Silica",
    "functions": [
      "점증",
      "흡착"
    ]
  },
  {
    "name": "소듐알지네이트",
    "inci": "Sodium Alginate",
    "functions": [
      "점증",
      "보습"
    ]
  },
  {
    "name": "PEG-150 펜타에리스리틸테트라스테아레이트",
    "inci": "PEG-150 Pentaerythrityl Tetrastearate",
    "functions": [
      "점증",
      "유화보조"
    ]
  },
  {
    "name": "소듐아크릴레이트코폴리머",
    "inci": "Sodium Acrylates Copolymer",
    "functions": [
      "점증"
    ]
  },
  {
    "name": "마그네슘알루미늄실리케이트",
    "inci": "Magnesium Aluminum Silicate",
    "functions": [
      "점증"
    ]
  },
  {
    "name": "폴리아크릴아마이드",
    "inci": "Polyacrylamide",
    "functions": [
      "점증",
      "유화보조"
    ]
  },
  {
    "name": "아크릴레이트/스테아레스-20메타크릴레이트코폴리머",
    "inci": "Acrylates/Steareth-20 Methacrylate Copolymer",
    "functions": [
      "점증"
    ]
  },
  {
    "name": "하이드록시에틸아크릴레이트/소듐아크릴로일디메틸타우레이트코폴리머",
    "inci": "Hydroxyethyl Acrylate/Sodium Acryloyldimethyl Taurate Copolymer",
    "functions": [
      "점증",
      "유화보조"
    ]
  },
  {
    "name": "트라가칸스검",
    "inci": "Tragacanth Gum",
    "functions": [
      "점증"
    ]
  },
  {
    "name": "소듐스타치글라이콜레이트",
    "inci": "Sodium Starch Glycolate",
    "functions": [
      "점증"
    ]
  },
  {
    "name": "소르비탄스테아레이트",
    "inci": "Sorbitan Stearate",
    "functions": [
      "유화"
    ]
  },
  {
    "name": "폴리솔베이트80",
    "inci": "Polysorbate 80",
    "functions": [
      "유화",
      "가용화"
    ]
  },
  {
    "name": "스테아레스-21",
    "inci": "Steareth-21",
    "functions": [
      "유화"
    ]
  },
  {
    "name": "세테아레스-12",
    "inci": "Ceteareth-12",
    "functions": [
      "유화"
    ]
  },
  {
    "name": "글리세릴스테아레이트시트레이트",
    "inci": "Glyceryl Stearate Citrate",
    "functions": [
      "유화"
    ]
  },
  {
    "name": "폴리글리세릴-3메틸글루코스디스테아레이트",
    "inci": "Polyglyceryl-3 Methylglucose Distearate",
    "functions": [
      "유화",
      "컨디셔닝"
    ]
  },
  {
    "name": "소듐세테아릴설페이트",
    "inci": "Sodium Cetearyl Sulfate",
    "functions": [
      "유화"
    ]
  },
  {
    "name": "라우릴글루코사이드",
    "inci": "Lauryl Glucoside",
    "functions": [
      "유화",
      "계면활성"
    ]
  },
  {
    "name": "베헤닐알코올",
    "inci": "Behenyl Alcohol",
    "functions": [
      "점증",
      "유화보조"
    ]
  },
  {
    "name": "폴리글리세릴-10스테아레이트",
    "inci": "Polyglyceryl-10 Stearate",
    "functions": [
      "유화"
    ]
  },
  {
    "name": "소듐스테아로일글루타메이트",
    "inci": "Sodium Stearoyl Glutamate",
    "functions": [
      "유화"
    ]
  },
  {
    "name": "세틸포스페이트",
    "inci": "Cetyl Phosphate",
    "functions": [
      "유화"
    ]
  },
  {
    "name": "포타슘세틸포스페이트",
    "inci": "Potassium Cetyl Phosphate",
    "functions": [
      "유화"
    ]
  },
  {
    "name": "폴리솔베이트85",
    "inci": "Polysorbate 85",
    "functions": [
      "유화"
    ]
  },
  {
    "name": "PEG-20글리세릴스테아레이트",
    "inci": "PEG-20 Glyceryl Stearate",
    "functions": [
      "유화"
    ]
  },
  {
    "name": "세테스-20",
    "inci": "Ceteth-20",
    "functions": [
      "유화"
    ]
  },
  {
    "name": "트레할로스",
    "inci": "Trehalose",
    "functions": [
      "보습"
    ]
  },
  {
    "name": "알란토인",
    "inci": "Allantoin",
    "functions": [
      "보습",
      "진정"
    ]
  },
  {
    "name": "소듐PCA",
    "inci": "Sodium PCA",
    "functions": [
      "보습"
    ]
  },
  {
    "name": "소듐폴리글루타메이트",
    "inci": "Sodium Polyglutamate",
    "functions": [
      "보습"
    ]
  },
  {
    "name": "베타글루칸",
    "inci": "Beta-Glucan",
    "functions": [
      "보습",
      "진정"
    ]
  },
  {
    "name": "세라마이드NP",
    "inci": "Ceramide NP",
    "functions": [
      "보습",
      "컨디셔닝"
    ]
  },
  {
    "name": "콜레스테롤",
    "inci": "Cholesterol",
    "functions": [
      "보습",
      "컨디셔닝"
    ]
  },
  {
    "name": "피토스핑고신",
    "inci": "Phytosphingosine",
    "functions": [
      "보습",
      "진정"
    ]
  },
  {
    "name": "히알루론산나트륨크로스폴리머",
    "inci": "Sodium Hyaluronate Crosspolymer",
    "functions": [
      "보습",
      "점증"
    ]
  },
  {
    "name": "가수분해히알루론산",
    "inci": "Hydrolyzed Hyaluronic Acid",
    "functions": [
      "보습"
    ]
  },
  {
    "name": "가수분해콜라겐",
    "inci": "Hydrolyzed Collagen",
    "functions": [
      "보습",
      "컨디셔닝"
    ]
  },
  {
    "name": "프럭토올리고당",
    "inci": "Fructooligosaccharides",
    "functions": [
      "보습"
    ]
  },
  {
    "name": "자일리톨",
    "inci": "Xylitol",
    "functions": [
      "보습"
    ]
  },
  {
    "name": "하이드로제네이티드전분가수분해물",
    "inci": "Hydrogenated Starch Hydrolysate",
    "functions": [
      "보습"
    ]
  },
  {
    "name": "세틸에틸헥사노에이트",
    "inci": "Cetyl Ethylhexanoate",
    "functions": [
      "에몰리언트"
    ]
  },
  {
    "name": "이소프로필미리스테이트",
    "inci": "Isopropyl Myristate",
    "functions": [
      "에몰리언트"
    ]
  },
  {
    "name": "이소프로필팔미테이트",
    "inci": "Isopropyl Palmitate",
    "functions": [
      "에몰리언트"
    ]
  },
  {
    "name": "옥틸도데칸올",
    "inci": "Octyldodecanol",
    "functions": [
      "에몰리언트"
    ]
  },
  {
    "name": "트리에틸헥사노인",
    "inci": "Triethylhexanoin",
    "functions": [
      "에몰리언트"
    ]
  },
  {
    "name": "코코카프릴레이트",
    "inci": "Coco-Caprylate",
    "functions": [
      "에몰리언트"
    ]
  },
  {
    "name": "네오펜틸글라이콜디헵타노에이트",
    "inci": "Neopentyl Glycol Diheptanoate",
    "functions": [
      "에몰리언트"
    ]
  },
  {
    "name": "다이카프릴릴카보네이트",
    "inci": "Dicaprylyl Carbonate",
    "functions": [
      "에몰리언트"
    ]
  },
  {
    "name": "마카다미아씨오일",
    "inci": "Macadamia Seed Oil",
    "functions": [
      "에몰리언트",
      "보습"
    ]
  },
  {
    "name": "아르간오일",
    "inci": "Argania Spinosa Kernel Oil",
    "functions": [
      "에몰리언트",
      "항산화"
    ]
  },
  {
    "name": "로즈힙오일",
    "inci": "Rosa Canina Fruit Oil",
    "functions": [
      "에몰리언트",
      "항산화"
    ]
  },
  {
    "name": "해바라기씨오일",
    "inci": "Helianthus Annuus Seed Oil",
    "functions": [
      "에몰리언트"
    ]
  },
  {
    "name": "올리브오일",
    "inci": "Olea Europaea Fruit Oil",
    "functions": [
      "에몰리언트",
      "항산화"
    ]
  },
  {
    "name": "코코넛오일",
    "inci": "Cocos Nucifera Oil",
    "functions": [
      "에몰리언트"
    ]
  },
  {
    "name": "아몬드오일",
    "inci": "Prunus Amygdalus Dulcis Oil",
    "functions": [
      "에몰리언트",
      "보습"
    ]
  },
  {
    "name": "동백오일",
    "inci": "Camellia Japonica Seed Oil",
    "functions": [
      "에몰리언트",
      "컨디셔닝"
    ]
  },
  {
    "name": "포도씨오일",
    "inci": "Vitis Vinifera Seed Oil",
    "functions": [
      "에몰리언트",
      "항산화"
    ]
  },
  {
    "name": "달맞이꽃오일",
    "inci": "Oenothera Biennis Oil",
    "functions": [
      "에몰리언트"
    ]
  },
  {
    "name": "미네랄오일",
    "inci": "Mineral Oil",
    "functions": [
      "에몰리언트"
    ]
  },
  {
    "name": "페트롤라툼",
    "inci": "Petrolatum",
    "functions": [
      "에몰리언트",
      "피막형성"
    ]
  },
  {
    "name": "소듐코코일이세치오네이트",
    "inci": "Sodium Cocoyl Isethionate",
    "functions": [
      "계면활성"
    ]
  },
  {
    "name": "디소듐라우레스설포석시네이트",
    "inci": "Disodium Laureth Sulfosuccinate",
    "functions": [
      "계면활성"
    ]
  },
  {
    "name": "라우라마이드DEA",
    "inci": "Lauramide DEA",
    "functions": [
      "계면활성",
      "점증"
    ]
  },
  {
    "name": "코카미도프로필하이드록시설테인",
    "inci": "Cocamidopropyl Hydroxysultaine",
    "functions": [
      "계면활성",
      "컨디셔닝"
    ]
  },
  {
    "name": "소듐라우로일사코시네이트",
    "inci": "Sodium Lauroyl Sarcosinate",
    "functions": [
      "계면활성"
    ]
  },
  {
    "name": "디소듐코코암포디아세테이트",
    "inci": "Disodium Cocoamphodiacetate",
    "functions": [
      "계면활성"
    ]
  },
  {
    "name": "라우릴베타인",
    "inci": "Lauryl Betaine",
    "functions": [
      "계면활성",
      "컨디셔닝"
    ]
  },
  {
    "name": "소듐라우릴설포아세테이트",
    "inci": "Sodium Lauryl Sulfoacetate",
    "functions": [
      "계면활성"
    ]
  },
  {
    "name": "암모늄라우릴설페이트",
    "inci": "Ammonium Lauryl Sulfate",
    "functions": [
      "계면활성"
    ]
  },
  {
    "name": "소듐C14-16올레핀설포네이트",
    "inci": "Sodium C14-16 Olefin Sulfonate",
    "functions": [
      "계면활성"
    ]
  },
  {
    "name": "카프릴릴/카프릴글루코사이드",
    "inci": "Caprylyl/Capryl Glucoside",
    "functions": [
      "계면활성"
    ]
  },
  {
    "name": "PEG-7글리세릴코코에이트",
    "inci": "PEG-7 Glyceryl Cocoate",
    "functions": [
      "계면활성",
      "가용화"
    ]
  },
  {
    "name": "소듐코코일글루타메이트",
    "inci": "Sodium Cocoyl Glutamate",
    "functions": [
      "계면활성"
    ]
  },
  {
    "name": "소듐라우로암포아세테이트",
    "inci": "Sodium Lauroamphoacetate",
    "functions": [
      "계면활성"
    ]
  },
  {
    "name": "소듐벤조에이트",
    "inci": "Sodium Benzoate",
    "functions": [
      "방부"
    ]
  },
  {
    "name": "포타슘소르베이트",
    "inci": "Potassium Sorbate",
    "functions": [
      "방부"
    ]
  },
  {
    "name": "벤질알코올",
    "inci": "Benzyl Alcohol",
    "functions": [
      "방부"
    ]
  },
  {
    "name": "데하이드로아세트산",
    "inci": "Dehydroacetic Acid",
    "functions": [
      "방부"
    ]
  },
  {
    "name": "클로르페네신",
    "inci": "Chlorphenesin",
    "functions": [
      "방부보조"
    ]
  },
  {
    "name": "카프릴하이드록사믹애씨드",
    "inci": "Caprylhydroxamic Acid",
    "functions": [
      "방부보조"
    ]
  },
  {
    "name": "소듐데하이드로아세테이트",
    "inci": "Sodium Dehydroacetate",
    "functions": [
      "방부"
    ]
  },
  {
    "name": "자몽씨추출물",
    "inci": "Citrus Grandis Seed Extract",
    "functions": [
      "방부보조",
      "항산화"
    ]
  },
  {
    "name": "메칠이소치아졸리논",
    "inci": "Methylisothiazolinone",
    "functions": [
      "방부"
    ]
  },
  {
    "name": "클로로자일레놀",
    "inci": "Chloroxylenol",
    "functions": [
      "방부"
    ]
  },
  {
    "name": "디아졸리디닐우레아",
    "inci": "Diazolidinyl Urea",
    "functions": [
      "방부"
    ]
  },
  {
    "name": "트리에탄올아민",
    "inci": "Triethanolamine",
    "functions": [
      "pH조절"
    ]
  },
  {
    "name": "소듐바이카보네이트",
    "inci": "Sodium Bicarbonate",
    "functions": [
      "pH조절"
    ]
  },
  {
    "name": "아미노메틸프로판올",
    "inci": "Aminomethyl Propanol",
    "functions": [
      "pH조절"
    ]
  },
  {
    "name": "인산",
    "inci": "Phosphoric Acid",
    "functions": [
      "pH조절"
    ]
  },
  {
    "name": "소듐시트레이트",
    "inci": "Sodium Citrate",
    "functions": [
      "pH조절"
    ]
  },
  {
    "name": "포타슘하이드록사이드",
    "inci": "Potassium Hydroxide",
    "functions": [
      "pH조절"
    ]
  },
  {
    "name": "아세트산",
    "inci": "Acetic Acid",
    "functions": [
      "pH조절"
    ]
  },
  {
    "name": "숙신산",
    "inci": "Succinic Acid",
    "functions": [
      "pH조절"
    ]
  },
  {
    "name": "아스코빌글루코사이드",
    "inci": "Ascorbyl Glucoside",
    "functions": [
      "항산화",
      "미백"
    ]
  },
  {
    "name": "소듐아스코빌포스페이트",
    "inci": "Sodium Ascorbyl Phosphate",
    "functions": [
      "항산화",
      "미백"
    ]
  },
  {
    "name": "아스코빌테트라이소팔미테이트",
    "inci": "Ascorbyl Tetraisopalmitate",
    "functions": [
      "항산화",
      "미백"
    ]
  },
  {
    "name": "페룰산",
    "inci": "Ferulic Acid",
    "functions": [
      "항산화"
    ]
  },
  {
    "name": "레스베라트롤",
    "inci": "Resveratrol",
    "functions": [
      "항산화"
    ]
  },
  {
    "name": "소듐메타바이설파이트",
    "inci": "Sodium Metabisulfite",
    "functions": [
      "항산화"
    ]
  },
  {
    "name": "녹차추출물",
    "inci": "Camellia Sinensis Leaf Extract",
    "functions": [
      "항산화",
      "진정"
    ]
  },
  {
    "name": "로즈마리잎추출물",
    "inci": "Rosmarinus Officinalis Leaf Extract",
    "functions": [
      "항산화"
    ]
  },
  {
    "name": "PEG-60하이드로제네이티드캐스터오일",
    "inci": "PEG-60 Hydrogenated Castor Oil",
    "functions": [
      "가용화"
    ]
  },
  {
    "name": "PEG-40스테아레이트",
    "inci": "PEG-40 Stearate",
    "functions": [
      "가용화"
    ]
  },
  {
    "name": "폴리솔베이트40",
    "inci": "Polysorbate 40",
    "functions": [
      "가용화"
    ]
  },
  {
    "name": "PPG-26-부테스-26",
    "inci": "PPG-26-Buteth-26",
    "functions": [
      "가용화"
    ]
  },
  {
    "name": "폴록사머407",
    "inci": "Poloxamer 407",
    "functions": [
      "가용화",
      "점증"
    ]
  },
  {
    "name": "소르비탄이소스테아레이트",
    "inci": "Sorbitan Isostearate",
    "functions": [
      "가용화",
      "유화"
    ]
  },
  {
    "name": "PEG-8",
    "inci": "PEG-8",
    "functions": [
      "가용화",
      "보습"
    ]
  },
  {
    "name": "글라이콜릭애씨드",
    "inci": "Glycolic Acid",
    "functions": [
      "AHA",
      "각질케어"
    ]
  },
  {
    "name": "락틱애씨드",
    "inci": "Lactic Acid",
    "functions": [
      "AHA",
      "각질케어",
      "보습"
    ]
  },
  {
    "name": "만델릭애씨드",
    "inci": "Mandelic Acid",
    "functions": [
      "AHA",
      "각질케어"
    ]
  },
  {
    "name": "말릭애씨드",
    "inci": "Malic Acid",
    "functions": [
      "AHA",
      "각질케어"
    ]
  },
  {
    "name": "타타릭애씨드",
    "inci": "Tartaric Acid",
    "functions": [
      "AHA",
      "각질케어"
    ]
  },
  {
    "name": "글루코노락톤",
    "inci": "Gluconolactone",
    "functions": [
      "PHA",
      "각질케어",
      "보습"
    ]
  },
  {
    "name": "락토바이오닉애씨드",
    "inci": "Lactobionic Acid",
    "functions": [
      "PHA",
      "각질케어",
      "보습"
    ]
  },
  {
    "name": "말토바이오닉애씨드",
    "inci": "Maltobionic Acid",
    "functions": [
      "PHA",
      "각질케어",
      "보습"
    ]
  },
  {
    "name": "살리실릭애씨드",
    "inci": "Salicylic Acid",
    "functions": [
      "BHA",
      "각질케어",
      "피지조절"
    ]
  },
  {
    "name": "베타인살리실레이트",
    "inci": "Betaine Salicylate",
    "functions": [
      "BHA",
      "각질케어"
    ]
  },
  {
    "name": "버드나무껍질추출물",
    "inci": "Salix Alba (Willow) Bark Extract",
    "functions": [
      "BHA",
      "각질케어"
    ]
  },
  {
    "name": "카프릴로일살리실릭애씨드",
    "inci": "Capryloyl Salicylic Acid",
    "functions": [
      "LHA",
      "각질케어"
    ]
  },
  {
    "name": "에칠헥실메톡시신나메이트",
    "inci": "Ethylhexyl Methoxycinnamate",
    "functions": [
      "자외선차단"
    ]
  },
  {
    "name": "옥토크릴렌",
    "inci": "Octocrylene",
    "functions": [
      "자외선차단"
    ]
  },
  {
    "name": "에칠헥실살리실레이트",
    "inci": "Ethylhexyl Salicylate",
    "functions": [
      "자외선차단"
    ]
  },
  {
    "name": "호모살레이트",
    "inci": "Homosalate",
    "functions": [
      "자외선차단"
    ]
  },
  {
    "name": "비스에칠헥실옥시페놀메톡시페닐트리아진",
    "inci": "Bis-Ethylhexyloxyphenol Methoxyphenyl Triazine",
    "functions": [
      "자외선차단"
    ]
  },
  {
    "name": "메칠렌비스벤조트리아졸릴테트라메칠부틸페놀",
    "inci": "Methylene Bis-Benzotriazolyl Tetramethylbutylphenol",
    "functions": [
      "자외선차단"
    ]
  },
  {
    "name": "디에칠아미노하이드록시벤조일헥실벤조에이트",
    "inci": "Diethylamino Hydroxybenzoyl Hexyl Benzoate",
    "functions": [
      "자외선차단"
    ]
  },
  {
    "name": "에칠헥실트리아존",
    "inci": "Ethylhexyl Triazone",
    "functions": [
      "자외선차단"
    ]
  },
  {
    "name": "드로메트리졸트리실록산",
    "inci": "Drometrizole Trisiloxane",
    "functions": [
      "자외선차단"
    ]
  },
  {
    "name": "이소아밀p-메톡시신나메이트",
    "inci": "Isoamyl p-Methoxycinnamate",
    "functions": [
      "자외선차단"
    ]
  },
  {
    "name": "폴리실리콘-15",
    "inci": "Polysilicone-15",
    "functions": [
      "자외선차단"
    ]
  },
  {
    "name": "벤조페논-3",
    "inci": "Benzophenone-3",
    "functions": [
      "자외선차단"
    ]
  },
  {
    "name": "티타늄디옥사이드",
    "inci": "Titanium Dioxide",
    "functions": [
      "자외선차단",
      "착색"
    ]
  },
  {
    "name": "징크옥사이드",
    "inci": "Zinc Oxide",
    "functions": [
      "자외선차단",
      "진정"
    ]
  },
  {
    "name": "나이아신아마이드",
    "inci": "Niacinamide",
    "functions": [
      "미백",
      "피지조절"
    ]
  },
  {
    "name": "알부틴",
    "inci": "Arbutin",
    "functions": [
      "미백"
    ]
  },
  {
    "name": "트라넥사믹애씨드",
    "inci": "Tranexamic Acid",
    "functions": [
      "미백"
    ]
  },
  {
    "name": "에칠아스코빌에텔",
    "inci": "Ethyl Ascorbyl Ether",
    "functions": [
      "미백",
      "항산화"
    ]
  },
  {
    "name": "3-O-에칠아스코르빅애씨드",
    "inci": "3-O-Ethyl Ascorbic Acid",
    "functions": [
      "미백",
      "항산화"
    ]
  },
  {
    "name": "감초추출물",
    "inci": "Glycyrrhiza Glabra Root Extract",
    "functions": [
      "미백",
      "진정"
    ]
  },
  {
    "name": "닥나무추출물",
    "inci": "Broussonetia Kazinoki Bark Extract",
    "functions": [
      "미백"
    ]
  },
  {
    "name": "뽕나무추출물",
    "inci": "Morus Alba Bark Extract",
    "functions": [
      "미백"
    ]
  },
  {
    "name": "유용성감초추출물",
    "inci": "Glycyrrhetinic Acid",
    "functions": [
      "미백",
      "진정"
    ]
  },
  {
    "name": "코직산",
    "inci": "Kojic Acid",
    "functions": [
      "미백"
    ]
  },
  {
    "name": "레티놀",
    "inci": "Retinol",
    "functions": [
      "주름개선"
    ]
  },
  {
    "name": "레티닐팔미테이트",
    "inci": "Retinyl Palmitate",
    "functions": [
      "주름개선"
    ]
  },
  {
    "name": "바쿠치올",
    "inci": "Bakuchiol",
    "functions": [
      "주름개선",
      "항산화"
    ]
  },
  {
    "name": "아데노신",
    "inci": "Adenosine",
    "functions": [
      "주름개선"
    ]
  },
  {
    "name": "팔미토일펜타펩타이드-4",
    "inci": "Palmitoyl Pentapeptide-4",
    "functions": [
      "주름개선"
    ]
  },
  {
    "name": "아세틸헥사펩타이드-8",
    "inci": "Acetyl Hexapeptide-8",
    "functions": [
      "주름개선"
    ]
  },
  {
    "name": "코퍼트라이펩타이드-1",
    "inci": "Copper Tripeptide-1",
    "functions": [
      "주름개선",
      "컨디셔닝"
    ]
  },
  {
    "name": "유비퀴논",
    "inci": "Ubiquinone",
    "functions": [
      "주름개선",
      "항산화"
    ]
  },
  {
    "name": "sh-올리고펩타이드-1",
    "inci": "sh-Oligopeptide-1",
    "functions": [
      "주름개선"
    ]
  },
  {
    "name": "레티날",
    "inci": "Retinal",
    "functions": [
      "주름개선"
    ]
  },
  {
    "name": "하이드록시피나콜론레티노에이트",
    "inci": "Hydroxypinacolone Retinoate",
    "functions": [
      "주름개선"
    ]
  },
  {
    "name": "병풀추출물",
    "inci": "Centella Asiatica Extract",
    "functions": [
      "진정",
      "컨디셔닝"
    ]
  },
  {
    "name": "마데카소사이드",
    "inci": "Madecassoside",
    "functions": [
      "진정"
    ]
  },
  {
    "name": "아시아티코사이드",
    "inci": "Asiaticoside",
    "functions": [
      "진정"
    ]
  },
  {
    "name": "비사보롤",
    "inci": "Bisabolol",
    "functions": [
      "진정"
    ]
  },
  {
    "name": "카모마일꽃추출물",
    "inci": "Chamomilla Recutita Flower Extract",
    "functions": [
      "진정"
    ]
  },
  {
    "name": "티트리잎추출물",
    "inci": "Melaleuca Alternifolia Leaf Extract",
    "functions": [
      "진정",
      "피지조절"
    ]
  },
  {
    "name": "어성초추출물",
    "inci": "Houttuynia Cordata Extract",
    "functions": [
      "진정"
    ]
  },
  {
    "name": "귀리커널추출물",
    "inci": "Avena Sativa Kernel Extract",
    "functions": [
      "진정",
      "보습"
    ]
  },
  {
    "name": "알로에베라잎추출물",
    "inci": "Aloe Barbadensis Leaf Extract",
    "functions": [
      "보습",
      "진정"
    ]
  },
  {
    "name": "향료",
    "inci": "Fragrance (Parfum)",
    "functions": [
      "향료"
    ]
  },
  {
    "name": "라벤더오일",
    "inci": "Lavandula Angustifolia Oil",
    "functions": [
      "향료",
      "진정"
    ]
  },
  {
    "name": "유칼립투스오일",
    "inci": "Eucalyptus Globulus Leaf Oil",
    "functions": [
      "향료"
    ]
  },
  {
    "name": "로즈마리잎오일",
    "inci": "Rosmarinus Officinalis Leaf Oil",
    "functions": [
      "향료",
      "항산화"
    ]
  },
  {
    "name": "레몬껍질오일",
    "inci": "Citrus Limon Peel Oil",
    "functions": [
      "향료"
    ]
  },
  {
    "name": "오렌지껍질오일",
    "inci": "Citrus Aurantium Dulcis Peel Oil",
    "functions": [
      "향료"
    ]
  },
  {
    "name": "자몽껍질오일",
    "inci": "Citrus Grandis Peel Oil",
    "functions": [
      "향료"
    ]
  },
  {
    "name": "베르가못오일",
    "inci": "Citrus Aurantium Bergamia Fruit Oil",
    "functions": [
      "향료"
    ]
  },
  {
    "name": "일랑일랑꽃오일",
    "inci": "Cananga Odorata Flower Oil",
    "functions": [
      "향료"
    ]
  },
  {
    "name": "제라늄오일",
    "inci": "Pelargonium Graveolens Oil",
    "functions": [
      "향료"
    ]
  },
  {
    "name": "자스민꽃오일",
    "inci": "Jasminum Officinale Flower Oil",
    "functions": [
      "향료"
    ]
  },
  {
    "name": "로즈꽃오일",
    "inci": "Rosa Damascena Flower Oil",
    "functions": [
      "향료"
    ]
  },
  {
    "name": "시더우드나무껍질오일",
    "inci": "Cedrus Atlantica Bark Oil",
    "functions": [
      "향료"
    ]
  },
  {
    "name": "마이카",
    "inci": "Mica",
    "functions": [
      "착색"
    ]
  },
  {
    "name": "산화철(적색)",
    "inci": "Iron Oxides (CI 77491)",
    "functions": [
      "착색"
    ]
  },
  {
    "name": "산화철(황색)",
    "inci": "Iron Oxides (CI 77492)",
    "functions": [
      "착색"
    ]
  },
  {
    "name": "산화철(흑색)",
    "inci": "Iron Oxides (CI 77499)",
    "functions": [
      "착색"
    ]
  },
  {
    "name": "울트라마린",
    "inci": "Ultramarines (CI 77007)",
    "functions": [
      "착색"
    ]
  },
  {
    "name": "적색40호",
    "inci": "Red 40 (CI 16035)",
    "functions": [
      "착색"
    ]
  },
  {
    "name": "황색5호",
    "inci": "Yellow 5 (CI 19140)",
    "functions": [
      "착색"
    ]
  },
  {
    "name": "청색1호",
    "inci": "Blue 1 (CI 42090)",
    "functions": [
      "착색"
    ]
  },
  {
    "name": "카민",
    "inci": "Carmine (CI 75470)",
    "functions": [
      "착색"
    ]
  },
  {
    "name": "비스머스옥시클로라이드",
    "inci": "Bismuth Oxychloride",
    "functions": [
      "착색",
      "펄"
    ]
  },
  {
    "name": "사이클로펜타실록산",
    "inci": "Cyclopentasiloxane",
    "functions": [
      "에몰리언트",
      "피막형성"
    ]
  },
  {
    "name": "사이클로헥사실록산",
    "inci": "Cyclohexasiloxane",
    "functions": [
      "에몰리언트"
    ]
  },
  {
    "name": "디메티콘크로스폴리머",
    "inci": "Dimethicone Crosspolymer",
    "functions": [
      "점증",
      "피막형성"
    ]
  },
  {
    "name": "페닐트리메티콘",
    "inci": "Phenyl Trimethicone",
    "functions": [
      "에몰리언트",
      "컨디셔닝"
    ]
  },
  {
    "name": "아모디메티콘",
    "inci": "Amodimethicone",
    "functions": [
      "컨디셔닝"
    ]
  },
  {
    "name": "PVP",
    "inci": "Polyvinylpyrrolidone",
    "functions": [
      "피막형성",
      "점증"
    ]
  },
  {
    "name": "PVP/VA코폴리머",
    "inci": "PVP/VA Copolymer",
    "functions": [
      "피막형성"
    ]
  },
  {
    "name": "아크릴레이트코폴리머",
    "inci": "Acrylates Copolymer",
    "functions": [
      "피막형성"
    ]
  },
  {
    "name": "폴리우레탄-39",
    "inci": "Polyurethane-39",
    "functions": [
      "피막형성",
      "점증"
    ]
  },
  {
    "name": "나이트로셀룰로오스",
    "inci": "Nitrocellulose",
    "functions": [
      "피막형성"
    ]
  },
  {
    "name": "디소듐이디티에이",
    "inci": "Disodium EDTA",
    "functions": [
      "킬레이팅"
    ]
  },
  {
    "name": "테트라소듐이디티에이",
    "inci": "Tetrasodium EDTA",
    "functions": [
      "킬레이팅"
    ]
  },
  {
    "name": "소듐파이테이트",
    "inci": "Sodium Phytate",
    "functions": [
      "킬레이팅"
    ]
  },
  {
    "name": "에티드로닉애씨드",
    "inci": "Etidronic Acid",
    "functions": [
      "킬레이팅"
    ]
  },
  {
    "name": "글루콘산",
    "inci": "Gluconic Acid",
    "functions": [
      "킬레이팅"
    ]
  },
  {
    "name": "카나우바왁스",
    "inci": "Copernicia Cerifera (Carnauba) Wax",
    "functions": [
      "왁스",
      "경도조절"
    ]
  },
  {
    "name": "칸데릴라왁스",
    "inci": "Euphorbia Cerifera (Candelilla) Wax",
    "functions": [
      "왁스",
      "경도조절"
    ]
  },
  {
    "name": "비즈왁스",
    "inci": "Beeswax (Cera Alba)",
    "functions": [
      "왁스",
      "에몰리언트"
    ]
  },
  {
    "name": "마이크로크리스탈린왁스",
    "inci": "Microcrystalline Wax",
    "functions": [
      "왁스",
      "경도조절"
    ]
  },
  {
    "name": "세레신",
    "inci": "Ceresin",
    "functions": [
      "왁스",
      "경도조절"
    ]
  },
  {
    "name": "파라핀",
    "inci": "Paraffin",
    "functions": [
      "왁스",
      "에몰리언트"
    ]
  },
  {
    "name": "폴리에틸렌",
    "inci": "Polyethylene",
    "functions": [
      "왁스",
      "점증"
    ]
  },
  {
    "name": "호호바에스터",
    "inci": "Jojoba Esters",
    "functions": [
      "왁스",
      "에몰리언트"
    ]
  },
  {
    "name": "아연피시에이",
    "inci": "Zinc PCA",
    "functions": [
      "피지조절"
    ]
  },
  {
    "name": "카올린",
    "inci": "Kaolin",
    "functions": [
      "피지조절",
      "점증"
    ]
  },
  {
    "name": "참숯가루",
    "inci": "Charcoal Powder",
    "functions": [
      "피지조절",
      "흡착"
    ]
  },
  {
    "name": "아연글루코네이트",
    "inci": "Zinc Gluconate",
    "functions": [
      "피지조절"
    ]
  },
  {
    "name": "세리사이트",
    "inci": "Sericite",
    "functions": [
      "피지조절",
      "점증"
    ]
  },
  {
    "name": "폴리쿼터늄-7",
    "inci": "Polyquaternium-7",
    "functions": [
      "컨디셔닝"
    ]
  },
  {
    "name": "폴리쿼터늄-10",
    "inci": "Polyquaternium-10",
    "functions": [
      "컨디셔닝",
      "점증"
    ]
  },
  {
    "name": "폴리쿼터늄-6",
    "inci": "Polyquaternium-6",
    "functions": [
      "컨디셔닝"
    ]
  },
  {
    "name": "세트리모늄클로라이드",
    "inci": "Cetrimonium Chloride",
    "functions": [
      "컨디셔닝",
      "계면활성"
    ]
  },
  {
    "name": "베헨트리모늄클로라이드",
    "inci": "Behentrimonium Chloride",
    "functions": [
      "컨디셔닝"
    ]
  },
  {
    "name": "가수분해케라틴",
    "inci": "Hydrolyzed Keratin",
    "functions": [
      "컨디셔닝",
      "보습"
    ]
  },
  {
    "name": "가수분해실크",
    "inci": "Hydrolyzed Silk",
    "functions": [
      "컨디셔닝",
      "보습"
    ]
  },
  {
    "name": "아르기닌",
    "inci": "Arginine",
    "functions": [
      "pH조절",
      "컨디셔닝"
    ]
  },
  {
    "name": "멘톨",
    "inci": "Menthol",
    "functions": [
      "청량감"
    ]
  },
  {
    "name": "캄퍼",
    "inci": "Camphor",
    "functions": [
      "청량감"
    ]
  },
  {
    "name": "판테닐에틸에텔",
    "inci": "Panthenyl Ethyl Ether",
    "functions": [
      "컨디셔닝"
    ]
  },
  {
    "name": "세라마이드EOP",
    "inci": "Ceramide EOP",
    "functions": [
      "보습",
      "컨디셔닝"
    ]
  },
  {
    "name": "탈크",
    "inci": "Talc",
    "functions": [
      "흡착",
      "점증"
    ]
  },
  {
    "name": "나일론-12",
    "inci": "Nylon-12",
    "functions": [
      "사용감개선"
    ]
  },
  {
    "name": "실리카",
    "inci": "Silica",
    "functions": [
      "흡착",
      "점증"
    ]
  },
  {
    "name": "보론나이트라이드",
    "inci": "Boron Nitride",
    "functions": [
      "사용감개선"
    ]
  },
  {
    "name": "마그네슘스테아레이트",
    "inci": "Magnesium Stearate",
    "functions": [
      "점증",
      "사용감개선"
    ]
  },
  {
    "name": "징크스테아레이트",
    "inci": "Zinc Stearate",
    "functions": [
      "점증"
    ]
  },
  {
    "name": "옥수수전분",
    "inci": "Corn Starch",
    "functions": [
      "흡착",
      "점증"
    ]
  },
  {
    "name": "감자전분",
    "inci": "Potato Starch",
    "functions": [
      "흡착"
    ]
  },
  {
    "name": "PMMA",
    "inci": "Polymethyl Methacrylate",
    "functions": [
      "사용감개선"
    ]
  },
  {
    "name": "실리카실릴레이트",
    "inci": "Silica Silylate",
    "functions": [
      "흡착"
    ]
  },
  {
    "name": "마그네슘아스코빌포스페이트",
    "inci": "Magnesium Ascorbyl Phosphate",
    "functions": [
      "미백",
      "항산화"
    ]
  },
  {
    "name": "세라마이드AP",
    "inci": "Ceramide AP",
    "functions": [
      "보습",
      "컨디셔닝"
    ]
  },
  {
    "name": "디포타슘글리시리제이트",
    "inci": "Dipotassium Glycyrrhizate",
    "functions": [
      "진정"
    ]
  },
  {
    "name": "스쿠알렌",
    "inci": "Squalene",
    "functions": [
      "에몰리언트"
    ]
  },
  {
    "name": "편백나무워터",
    "inci": "Chamaecyparis Obtusa Water",
    "functions": [
      "보습",
      "향료"
    ]
  },
  {
    "name": "병풀워터",
    "inci": "Centella Asiatica Water",
    "functions": [
      "보습",
      "진정"
    ]
  },
  {
    "name": "다마스크장미꽃수",
    "inci": "Rosa Damascena Flower Water",
    "functions": [
      "보습",
      "향료"
    ]
  },
  {
    "name": "위치하젤수",
    "inci": "Hamamelis Virginiana Water",
    "functions": [
      "진정",
      "피지조절"
    ]
  },
  {
    "name": "히알루론산나트륨(저분자)",
    "inci": "Sodium Hyaluronate (Low Molecular Weight)",
    "functions": [
      "보습"
    ]
  },
  {
    "name": "히알루론산나트륨(고분자)",
    "inci": "Sodium Hyaluronate (High Molecular Weight)",
    "functions": [
      "보습",
      "점증"
    ]
  },
  {
    "name": "스테아레스-2",
    "inci": "Steareth-2",
    "functions": [
      "유화"
    ]
  },
  {
    "name": "라우레스-4",
    "inci": "Laureth-4",
    "functions": [
      "유화",
      "가용화"
    ]
  },
  {
    "name": "코카미드MEA",
    "inci": "Cocamide MEA",
    "functions": [
      "점증",
      "계면활성"
    ]
  },
  {
    "name": "코카미드DEA",
    "inci": "Cocamide DEA",
    "functions": [
      "점증",
      "계면활성"
    ]
  },
  {
    "name": "소듐메칠코코일타우레이트",
    "inci": "Sodium Methyl Cocoyl Taurate",
    "functions": [
      "계면활성"
    ]
  },
  {
    "name": "디소듐코코암포디프로피오네이트",
    "inci": "Disodium Cocoamphodipropionate",
    "functions": [
      "계면활성"
    ]
  }
]

# --------------------------------------------------------------------------
# 로컬 스토리지 (브라우저별 저장 - 기존 HTML 버전과 동일하게 사용자간 데이터는 공유되지 않습니다)
# --------------------------------------------------------------------------
local_storage = LocalStorage()


def _new_id() -> str:
    return "ing_" + uuid.uuid4().hex[:10]


def load_ingredients():
    raw = local_storage.getItem(STORAGE_KEY)
    if raw:
        try:
            data = json.loads(raw) if isinstance(raw, str) else raw
            if isinstance(data, list) and len(data) > 0:
                return data
        except Exception:
            pass
    return [{"id": _new_id(), **item} for item in DEFAULT_INGREDIENTS]


def persist():
    local_storage.setItem(STORAGE_KEY, json.dumps(st.session_state.ingredients, ensure_ascii=False))


if "ingredients" not in st.session_state:
    st.session_state.ingredients = load_ingredients()
    persist()

if "editing_id" not in st.session_state:
    st.session_state.editing_id = None


def normalize(fn: str) -> str:
    return fn.strip().lower()


def find_by_name(name: str):
    for ing in st.session_state.ingredients:
        if ing["name"] == name:
            return ing
    return None


def render_tags(functions, matched=None, as_html=True):
    matched = matched or []
    spans = []
    for f in functions:
        cls = "tag match" if f in matched else "tag"
        spans.append(f'<span class="{cls}">{f}</span>')
    return " ".join(spans)


# --------------------------------------------------------------------------
# 헤더
# --------------------------------------------------------------------------
st.markdown(
    """
    <div style="text-align:center; margin-bottom: 10px;">
        <h1 style="margin-bottom:4px;">🧪 대체원료 파인더</h1>
        <p style="color:#607d8b; font-size:14px;">
            원료 하나를 제외하면, 기능이 겹치는 대체 후보를 자동으로 찾아 정리해주는 처방 보조 도구
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# ① 제외할 원료 선택
# --------------------------------------------------------------------------
st.subheader("① 제외할 원료 선택")

ingredient_names = [i["name"] for i in st.session_state.ingredients]

selected_name = st.selectbox(
    "원료명을 입력하거나 선택하세요 (예: 잔탄검)",
    options=ingredient_names,
    index=None,
    placeholder="원료명 검색...",
    key="exclude_input",
)

target = find_by_name(selected_name) if selected_name else None

if selected_name and not target:
    st.info(f"'{selected_name}' 원료를 목록에서 찾을 수 없습니다. 아래 '원료 데이터 관리'에서 추가해주세요.")
elif target:
    st.markdown(
        f"""
        <div class="selected-box">
            <div class="name">{target['name']}</div>
            <div class="inci">{target.get('inci', '')}</div>
            <div>{render_tags(target['functions'])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --------------------------------------------------------------------------
# ② 대체 후보 (기능 일치 개수 순)
# --------------------------------------------------------------------------
st.subheader("② 대체 후보 (기능 일치 개수 순)")

if not target:
    st.caption("위에서 제외할 원료를 먼저 선택해주세요.")
else:
    target_fns_norm = [normalize(f) for f in target["functions"]]

    candidates = []
    for ing in st.session_state.ingredients:
        if ing["id"] == target["id"]:
            continue
        ing_fns_norm = [normalize(f) for f in ing["functions"]]
        matched_fns = [f for f in ing["functions"] if normalize(f) in target_fns_norm]
        missing_fns = [f for f in target["functions"] if normalize(f) not in ing_fns_norm]
        if matched_fns:
            candidates.append(
                {
                    "ing": ing,
                    "match_count": len(matched_fns),
                    "matched_fns": matched_fns,
                    "missing_fns": missing_fns,
                }
            )

    candidates.sort(key=lambda c: (-c["match_count"], c["ing"]["name"]))

    if not candidates:
        st.caption("기능이 겹치는 대체 후보가 없습니다. 원료 데이터를 보강해보세요.")
    else:
        rows_html = ""
        for c in candidates:
            ing = c["ing"]
            is_full = len(c["missing_fns"]) == 0
            badge = (
                '<span class="badge full">완전 대체</span>'
                if is_full
                else f'<span class="badge partial">부분 대체 {c["match_count"]}/{len(target["functions"])}</span>'
            )
            tags_html = render_tags(ing["functions"], matched=c["matched_fns"])
            rows_html += f"""
                <tr>
                    <td><strong>{ing['name']}</strong></td>
                    <td>{ing.get('inci', '')}</td>
                    <td>{tags_html}</td>
                    <td><span class="count">{c['match_count']}</span></td>
                    <td>{badge}</td>
                </tr>
            """

        table_html = f"""
        <div style="overflow-x:auto;">
        <table class="result-table">
            <thead>
                <tr><th>원료명</th><th>INCI명</th><th>기능 (● 일치)</th><th>일치개수</th><th>대체 가능성</th></tr>
            </thead>
            <tbody>{rows_html}</tbody>
        </table>
        </div>
        """
        st.markdown(table_html, unsafe_allow_html=True)

# --------------------------------------------------------------------------
# ③ 원료 데이터 관리 (추가 / 수정 / 삭제)
# --------------------------------------------------------------------------
with st.expander("③ 원료 데이터 관리 (추가 / 수정 / 삭제)"):

    # ---- 툴바: 내보내기 / 불러오기 / 초기화 ----
    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            "JSON 내보내기",
            data=json.dumps(st.session_state.ingredients, ensure_ascii=False, indent=2),
            file_name="대체원료_데이터.json",
            mime="application/json",
            use_container_width=True,
        )

    with col2:
        uploaded = st.file_uploader("JSON 불러오기", type="json", label_visibility="collapsed")
        if uploaded is not None:
            try:
                data = json.load(uploaded)
                if not isinstance(data, list) or not all("name" in d and "functions" in d for d in data):
                    raise ValueError("형식이 올바르지 않습니다.")
                st.session_state.ingredients = [
                    {
                        "id": d.get("id") or _new_id(),
                        "name": d["name"],
                        "inci": d.get("inci", ""),
                        "functions": d["functions"],
                    }
                    for d in data
                ]
                persist()
                st.success(f"{len(data)}개의 원료 데이터를 불러왔습니다.")
                st.rerun()
            except Exception as e:
                st.error(f"파일을 불러오지 못했습니다: {e}")

    with col3:
        confirm_reset = st.checkbox("초기화 확인", key="confirm_reset")
        if st.button("기본 데이터로 초기화", use_container_width=True, disabled=not confirm_reset):
            st.session_state.ingredients = [{"id": _new_id(), **item} for item in DEFAULT_INGREDIENTS]
            persist()
            st.success("기본 데이터로 초기화되었습니다.")
            st.rerun()

    st.divider()

    # ---- 추가 / 수정 폼 ----
    editing = None
    if st.session_state.editing_id:
        editing = next((i for i in st.session_state.ingredients if i["id"] == st.session_state.editing_id), None)

    with st.form("ingredient_form", clear_on_submit=not editing):
        f_col1, f_col2, f_col3 = st.columns([1, 1, 1.4])
        with f_col1:
            form_name = st.text_input("원료명", value=editing["name"] if editing else "", placeholder="예: 잔탄검")
        with f_col2:
            form_inci = st.text_input(
                "INCI명 (선택)", value=editing.get("inci", "") if editing else "", placeholder="예: Xanthan Gum"
            )
        with f_col3:
            form_functions = st.text_input(
                "기능 (쉼표로 구분)",
                value=", ".join(editing["functions"]) if editing else "",
                placeholder="예: 점증, 보습",
            )

        submit_label = "수정 완료" if editing else "추가"
        submitted = st.form_submit_button(submit_label)

        if submitted:
            name = form_name.strip()
            functions = [f.strip() for f in form_functions.split(",") if f.strip()]

            if not name:
                st.error("원료명을 입력해주세요.")
            elif not functions:
                st.error("기능을 1개 이상 입력해주세요. (쉼표로 구분)")
            else:
                if editing:
                    editing["name"] = name
                    editing["inci"] = form_inci.strip()
                    editing["functions"] = functions
                    st.session_state.editing_id = None
                else:
                    st.session_state.ingredients.append(
                        {"id": _new_id(), "name": name, "inci": form_inci.strip(), "functions": functions}
                    )
                persist()
                st.rerun()

    if editing:
        if st.button("수정 취소"):
            st.session_state.editing_id = None
            st.rerun()

    st.divider()

    # ---- 원료 목록 테이블 ----
    if not st.session_state.ingredients:
        st.caption("등록된 원료가 없습니다.")
    else:
        header_cols = st.columns([2, 2.4, 3, 1, 1])
        for col, label in zip(header_cols, ["원료명", "INCI명", "기능", "", ""]):
            col.markdown(f"**{label}**")

        for ing in st.session_state.ingredients:
            row_cols = st.columns([2, 2.4, 3, 1, 1])
            row_cols[0].write(ing["name"])
            row_cols[1].write(ing.get("inci", ""))
            row_cols[2].markdown(render_tags(ing["functions"]), unsafe_allow_html=True)
            if row_cols[3].button("수정", key=f"edit_{ing['id']}"):
                st.session_state.editing_id = ing["id"]
                st.rerun()
            if row_cols[4].button("삭제", key=f"del_{ing['id']}"):
                st.session_state.ingredients = [
                    i for i in st.session_state.ingredients if i["id"] != ing["id"]
                ]
                persist()
                st.rerun()
