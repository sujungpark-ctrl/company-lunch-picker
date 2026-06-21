import streamlit as st
import random
import time

st.title("🏢 우리 회사 전용 점심 메뉴 해결사 (거리 필터 추가!)")
st.write("출근 멤버의 취향과 오늘 날씨(거리)까지 고려하는 완벽한 솔루션입니다.")

st.divider()

# 1. 실제 자주 가는 식당 데이터베이스
menu_db = {
    "한식/든든한 국물 🍚": [
        "24시전주콩나물국밥", "담미온", "무청감자탕", "본가큰댁설렁탕", 
        "서소문", "밀본", "육전국밥", "뚝섬도락", "칼(칼국수)", 
        "프리미엄직원식당(한식뷔페)", "마시쏘(부대찌개)", "완백(부대찌개)"
    ],
    "중식 🐼": ["신신원", "달구벌반점"],
    "일식 🍣": ["오늘동", "멘쿠도"],
    "샐러드/샌드위치 🥗": ["쉭앤칙카페", "피쉬버켓", "써브웨이"],
    "패스트푸드 🍔": ["프랭크버거", "롯데리아"]
}

# 2. 🗺️ 식당별 거리 데이터베이스 구축 (보내주신 리스트 기준)
distance_db = {
    "close": [
        "신신원", "뚝섬도락", "달구벌반점", "오늘동", 
        "쉭앤칙카페", "피쉬버켓", "프랭크버거"
    ],
    "medium": [
        "24시전주콩나물국밥", "담미온", "무청감자탕", "본가큰댁설렁탕", 
        "칼(칼국수)", "프리미엄직원식당(한식뷔페)", "완백(부대찌개)", 
        "멘쿠도", "써브웨이", "롯데리아"
    ],
    "far": [
        "서소문", "밀본", "육전국밥", "마시쏘(부대찌개)"
    ]
}

# 3. 직원별 절대 안 가는 식당 블랙리스트
veto_db = {
    "오연식": ["칼(칼국수)"],
    "오민경": ["프랭크버거", "프리미엄직원식당"],
    "윤유진": ["서소문"]
}

# --- 필터 영역 시작 ---

# 기능 A: 오늘 출근 인원 체크
st.subheader("👥 오늘 함께 점심 먹는 멤버")
present_members = st.multiselect(
    "오늘 출근한 멤버들을 선택해 주세요:",
    list(veto_db.keys())
)

blacklisted_restaurants = set()
for member in present_members:
    for restaurant in veto_db[member]:
        blacklisted_restaurants.add(restaurant)

# 기능 B: ☀️ 오늘 날씨 및 거리 필터 (새로 추가됨!)
st.subheader("🌦️ 오늘 날씨나 컨디션은 어떤가요?")
weather_choice = st.radio(
    "허용 가능한 이동 범위를 골라주세요:",
    [
        "상관없음 (날씨 굿! 멀리 산책 겸 나가도 좋아) ☀️",
        "중간 거리까지만 (적당히 걸어갈 만한 곳) 🚶‍♂️",
        "무조건 가까운 곳 (비, 눈, 폭염, 한파, 귀찮음 극대화) ☔🥵"
    ]
)

# 선택된 날씨에 따라 허용할 거리 지정
allowed_distances = ["close"] # 가까운 곳은 무조건 포함
if "상관없음" in weather_choice or "중간 거리" in weather_choice:
    allowed_distances.append("medium")
if "상관없음" in weather_choice:
    allowed_distances.append("far")

# 기능 C: 오늘 피하고 싶은 메뉴 종류 선택
st.subheader("🙅‍♂️ 오늘 피하고 싶은 메뉴 종류가 있나요?")
exclude_categories = st.multiselect(
    "물리는 메뉴 종류는 체크해서 제외해 주세요:",
    list(menu_db.keys())
)

# --- 최종 후보군 필터링 조립 ---
final_candidates = []

for category, restaurants in menu_db.items():
    # 1. 카테고리 필터 통과 체크
    if category not in exclude_categories:
        for res in restaurants:
            # 2. 직원 블랙리스트 통과 체크
            if res not in blacklisted_restaurants:
                # 3. 거리 필터 통과 체크 (해당 식당의 거리가 허용된 거리에 포함되는지)
                is_allowed_distance = False
                for dist_type in allowed_distances:
                    if res in distance_db[dist_type]:
                        is_allowed_distance = True
                
                if is_allowed_distance:
                    final_candidates.append(res)

st.divider()

# 4. 운명의 룰렛 돌리기
st.subheader("🎲 오늘의 점심 운명은?")

# 현재 남은 후보 식당 개수 보여주기
st.write(f"💡 현재 필터링을 통과한 맛집 후보: **{len(final_candidates)}개**")

if len(final_candidates) > 0:
    if st.button("🚀 맛집 무작위 추첨 시작!!", use_container_width=True):
        
        status_text = st.empty()
        for _ in range(10):
            temp_pick = random.choice(final_candidates)
            status_text.info(f"🔍 [안전 필터링 중] 후보 탐색 👉 {temp_pick}")
            time.sleep(0.1)
            
        with st.spinner("최종 결정 중... 두구두구..."):
            time.sleep(0.8)
            selected_restaurant = random.choice(final_candidates)
            
        status_text.empty() 
        st.success(f"🎉 오늘 점심은 **[{selected_restaurant}]** 입니다!!")
        
        # 안내 문구에 거리 정보 깨알 노출
        res_dist = ""
        if selected_restaurant in distance_db["close"]: res_dist = "가까운"
        elif selected_restaurant in distance_db["medium"]: res_dist = "적당한 거리의"
        else: res_dist = "조금 먼"
        
        st.info(f"📍 [{selected_restaurant}]은(는) 우리 사무실에서 **{res_dist} 곳**에 있습니다. 조심히 다녀오세요!")
        st.balloons() 
else:
    st.error("조건을 너무 까다롭게 걸어서 갈 수 있는 식당이 없습니다! 조건을 완화해 주세요.")