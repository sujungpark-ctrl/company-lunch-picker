import streamlit as st
import random
import time
from datetime import date

# --- 세션 상태(Session State) 초기화 (새로 추가된 핵심 기능) ---
# 1. 오늘 날짜 저장 (날짜가 바뀌면 리셋하기 위함)
if "today_date" not in st.session_state:
    st.session_state.today_date = date.today()

# 날짜가 어제랑 다르면(즉, 하루가 지났으면) 임시 제외 목록 초기화
if st.session_state.today_date != date.today():
    st.session_state.today_date = date.today()
    st.session_state.temp_rejected = set()

# 2. 오늘 하루 동안 임시로 제외할 식당 목록
if "temp_rejected" not in st.session_state:
    st.session_state.temp_rejected = set()

# 3. 마지막으로 뽑힌 식당 저장
if "last_picked" not in st.session_state:
    st.session_state.last_picked = None
# -----------------------------------------------------------------

st.title("🏢 점심 메뉴 추천")
st.write("이래도 칭얼거릴거 다 안다")

st.divider()

# 1. 실제 자주 가는 식당 데이터베이스
menu_db = {
    "한식 🍚": [
        "24시전주콩나물국밥", "담미온", "무청감자탕", "본가큰댁설렁탕", 
        "서소문", "밀본", "육전국밥", "뚝섬도락", "칼(칼국수)", 
        "프리미엄직원식당(한식뷔페)", "마시쏘(부대찌개)", "완백(부대찌개)",
        "왕분식", "골목식당"
    ],
    "중식 🐼": ["신신원", "달구벌반점"],
    "일식 🍣": ["오늘동", "멘쿠도"],
    "샐러드/샌드위치 🥗": ["쉭앤칙카페", "피쉬버켓", "써브웨이"],
    "패스트푸드 🍔": ["프랭크버거", "롯데리아"]
}

# 2. 🗺️ 식당별 거리 데이터베이스
distance_db = {
    "close": [
        "신신원", "뚝섬도락", "달구벌반점", "오늘동", 
        "쉭앤칙카페", "피쉬버켓", "프랭크버거"
    ],
    "medium": [
        "24시전주콩나물국밥", "담미온", "무청감자탕", "본가큰댁설렁탕", 
        "칼(칼국수)", "프리미엄직원식당(한식뷔페)", "완백(부대찌개)", 
        "멘쿠도", "써브웨이", "롯데리아", "왕분식", "골목식당"
    ],
    "far": [
        "서소문", "밀본", "육전국밥", "마시쏘(부대찌개)"
    ]
}

# 3. 💵 결제 수단 데이터베이스 (현금 결제만 가능한 곳)
cash_only_list = ["뚝섬도락", "왕분식", "골목식당", "완백(부대찌개)"]

# 4. 직원별 절대 안 가는 식당 블랙리스트
veto_db = {
    "오연식": ["칼(칼국수)"],
    "오민경": ["프리미엄직원식당(한식뷔페)"],
    "윤유진": ["서소문"]
}

# --- 필터 영역 시작 ---

# 기능 A: 오늘 출근 인원 체크
st.subheader("👥 인물별 블랙리스트")
present_members = st.multiselect(
    "오늘 출근한 멤버들을 선택해 주세요:",
    list(veto_db.keys())
)

blacklisted_restaurants = set()
for member in present_members:
    for restaurant in veto_db[member]:
        blacklisted_restaurants.add(restaurant)

# 기능 B: 오늘 날씨 및 거리 필터
st.subheader("🌦️ 거리 허용범위")
weather_choice = st.radio(
    "허용 가능한 이동 범위를 골라주세요:",
    [
        "상관없음",
        "중간 거리까지만 ",
        "무조건 가까운 곳 (비, 눈, 폭염, 한파, 귀찮음 극대화) ☔🥵"
    ]
)

allowed_distances = ["close"] 
if "상관없음" in weather_choice or "중간 거리" in weather_choice:
    allowed_distances.append("medium")
if "상관없음" in weather_choice:
    allowed_distances.append("far")

# 기능 C: 💳 결제 수단 필터
st.subheader("💳 결제 수단")
payment_choice = st.radio(
    "식권대장 어플 사용 여부를 선택해 주세요:",
    [
        "상관없음 (현금 결제도 가능!) 💵",
        "식권대장 결제 가능 매장만 보기 📱"
    ]
)

# 기능 D: 오늘 피하고 싶은 메뉴 종류 선택
st.subheader("🙅‍♂️ 오늘 피하고 싶은 카테고리")
exclude_categories = st.multiselect(
    "물리는 메뉴 종류는 체크해서 제외해 주세요:",
    list(menu_db.keys())
)

# --- 최종 후보군 필터링 조립 ---
final_candidates = []

for category, restaurants in menu_db.items():
    if category not in exclude_categories:
        for res in restaurants:
            # 직원 블랙리스트 필터 + "오늘 한 번 까인 식당" 필터 동시 적용
            if res not in blacklisted_restaurants and res not in st.session_state.temp_rejected:
                is_allowed_distance = False
                for dist_type in allowed_distances:
                    if res in distance_db[dist_type]:
                        is_allowed_distance = True
                
                if is_allowed_distance:
                    if "식권대장 결제 가능" in payment_choice and res in cash_only_list:
                        continue
                    final_candidates.append(res)

st.divider()

# --- 현재 임시 제외된 식당 현황 보여주기 (옵션) ---
if st.session_state.temp_rejected:
    st.caption(f"🚫 오늘 맘에 안 들어서 쳐낸 식당들: {', '.join(st.session_state.temp_rejected)} (내일이면 다시 부활합니다)")

# 5. 운명의 룰렛 돌리기
st.subheader("🎲 오늘의 점심 운명은?")
st.write(f"💡 현재 모든 필터를 통과한 맛집 후보: **{len(final_candidates)}개**")

if len(final_candidates) > 0:
    if st.button("🚀 맛집 무작위 추첨 시작!!", use_container_width=True):
        
        status_text = st.empty()
        for _ in range(10):
            temp_pick = random.choice(final_candidates)
            status_text.info(f"🔍 [식권/거리 필터 작동 중] 후보 탐색 👉 {temp_pick}")
            time.sleep(0.1)
            
        with st.spinner("최종 결정 중... 두구두구..."):
            time.sleep(0.8)
            # 추첨 결과를 session_state에 저장
            st.session_state.last_picked = random.choice(final_candidates)
            
        status_text.empty() 

    # 추첨된 식당이 존재하면 결과 창과 '다시 뽑기' 버튼 표시
    if st.session_state.last_picked:
        selected_restaurant = st.session_state.last_picked
        st.success(f"🎉 오늘 점심은 **[{selected_restaurant}]** 입니다!!")
        
        if selected_restaurant in cash_only_list:
            st.warning(f"⚠️ 주의: [{selected_restaurant}]은(는) 현금(또는 개인 결제) 매장입니다! 식권대장 사용이 불가합니다.")
        else:
            st.info(f"📱 확인: [{selected_restaurant}]은(는) 식권대장 어플 결제가 가능한 매장입니다.")
            
        # 맘에 안 들 경우 다시 뽑는 버튼
        if st.button("👎 아 이건 좀... (이 식당 제외하고 다시 추첨)", type="primary", use_container_width=True):
            st.session_state.temp_rejected.add(selected_restaurant) # 임시 블랙리스트에 추가
            st.session_state.last_picked = None # 현재 픽 초기화
            st.rerun() # 화면 새로고침하여 즉시 반영

else:
    st.error("조건이 너무 엄격하거나 후보 식당을 다 까버려서 남은 식당이 없습니다! 조건을 완화해 주세요.")