import streamlit as st
import cv2
import numpy as np
import time
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="THE UNSEEN - Mystery Challenge",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# SETTINGS
# =========================================================

IMAGE_1_PATH = "images/mystery_room_1.png"
IMAGE_2_PATH = "images/mystery_room_2.png"

DISPLAY_WIDTH = 520
TIME_LIMIT = 60
POINTS_PER_DIFFERENCE = 10
MAX_DIFFERENCES = 20


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
        radial-gradient(
            circle at top,
            #1d3557 0%,
            #0b1320 45%,
            #05080d 100%
        );
        color: white;
    }

    .main-title {
        text-align: center;
        font-size: 46px;
        font-weight: 900;
        letter-spacing: 5px;
        margin-top: 10px;
        margin-bottom: 5px;
        color: #ffffff;
    }

    .subtitle {
        text-align: center;
        font-size: 17px;
        letter-spacing: 3px;
        color: #a9c7e8;
        margin-bottom: 25px;
    }

    .success-message {
        text-align: center;
        background: rgba(0, 255, 150, 0.12);
        border: 1px solid rgba(0, 255, 150, 0.5);
        border-radius: 12px;
        padding: 12px;
        color: #7dffbf;
        font-size: 18px;
        font-weight: bold;
        margin: 15px 0;
    }

    .wrong-message {
        text-align: center;
        background: rgba(255, 60, 60, 0.12);
        border: 1px solid rgba(255, 60, 60, 0.5);
        border-radius: 12px;
        padding: 12px;
        color: #ff8d8d;
        font-size: 18px;
        font-weight: bold;
        margin: 15px 0;
    }

    .info-box {
        text-align: center;
        background: rgba(255,255,255,0.06);
        border-radius: 15px;
        padding: 18px;
        margin: 20px 0;
    }

    div.stButton > button {
        border-radius: 12px;
        font-weight: bold;
        padding: 10px 25px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "regions": [],
    "game_started": False,
    "game_paused": False,
    "game_finished": False,
    "score": 0,
    "found_regions": [],
    "start_time": None,
    "pause_time": None,
    "total_paused_time": 0,
    "message": "",
    "message_type": "",
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# LOAD IMAGES
# =========================================================

try:

    image1 = Image.open(
        IMAGE_1_PATH
    ).convert("RGB")

    image2 = Image.open(
        IMAGE_2_PATH
    ).convert("RGB")

except Exception:

    st.error("❌ Images not found!")

    st.write(
        "Make sure these files exist:"
    )

    st.code(
        """
images/mystery_room_1.png
images/mystery_room_2.png
        """
    )

    st.stop()


# =========================================================
# RESIZE IMAGE
# =========================================================

def resize_image(image):

    width, height = image.size

    ratio = DISPLAY_WIDTH / width

    new_height = int(
        height * ratio
    )

    return image.resize(
        (
            DISPLAY_WIDTH,
            new_height
        )
    )


img1 = resize_image(image1)
img2 = resize_image(image2)


# =========================================================
# DIFFERENCE DETECTION
# =========================================================

def detect_differences(image_a, image_b):

    a = np.array(image_a)
    b = np.array(image_b)

    height = min(
        a.shape[0],
        b.shape[0]
    )

    width = min(
        a.shape[1],
        b.shape[1]
    )

    a = a[:height, :width]
    b = b[:height, :width]

    # -----------------------------------------------------
    # GRAYSCALE
    # -----------------------------------------------------

    gray_a = cv2.cvtColor(
        a,
        cv2.COLOR_RGB2GRAY
    )

    gray_b = cv2.cvtColor(
        b,
        cv2.COLOR_RGB2GRAY
    )

    # -----------------------------------------------------
    # ABSOLUTE DIFFERENCE
    # Lower threshold catches smaller differences
    # -----------------------------------------------------

    difference = cv2.absdiff(
        gray_a,
        gray_b
    )

    _, threshold = cv2.threshold(
        difference,
        20,
        255,
        cv2.THRESH_BINARY
    )

    # -----------------------------------------------------
    # MORPHOLOGY
    # Keep small objects visible
    # -----------------------------------------------------

    small_kernel = np.ones(
        (3, 3),
        np.uint8
    )

    threshold = cv2.morphologyEx(
        threshold,
        cv2.MORPH_OPEN,
        small_kernel
    )

    threshold = cv2.morphologyEx(
        threshold,
        cv2.MORPH_CLOSE,
        small_kernel
    )

    threshold = cv2.dilate(
        threshold,
        small_kernel,
        iterations=1
    )

    # -----------------------------------------------------
    # CONTOURS
    # -----------------------------------------------------

    contours, _ = cv2.findContours(
        threshold,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    regions = []

    image_area = width * height

    for contour in contours:

        x, y, w, h = cv2.boundingRect(
            contour
        )

        area = w * h

        # Allow smaller differences
        if area < 40:
            continue

        # Ignore very large regions
        if area > image_area * 0.20:
            continue

        # -------------------------------------------------
        # CLICKABLE PADDING
        # -------------------------------------------------

        padding = 25

        x1 = max(
            0,
            x - padding
        )

        y1 = max(
            0,
            y - padding
        )

        x2 = min(
            width,
            x + w + padding
        )

        y2 = min(
            height,
            y + h + padding
        )

        regions.append(
            (
                x1,
                y1,
                x2,
                y2
            )
        )

    # -----------------------------------------------------
    # MERGE OVERLAPPING REGIONS
    # -----------------------------------------------------

    merged = []

    for region in regions:

        x1, y1, x2, y2 = region

        merged_with_existing = False

        for i, existing in enumerate(
            merged
        ):

            ex1, ey1, ex2, ey2 = existing

            intersection_x1 = max(
                x1,
                ex1
            )

            intersection_y1 = max(
                y1,
                ey1
            )

            intersection_x2 = min(
                x2,
                ex2
            )

            intersection_y2 = min(
                y2,
                ey2
            )

            if (
                intersection_x2 > intersection_x1
                and
                intersection_y2 > intersection_y1
            ):

                intersection_area = (
                    intersection_x2
                    - intersection_x1
                ) * (
                    intersection_y2
                    - intersection_y1
                )

                region_area = (
                    x2 - x1
                ) * (
                    y2 - y1
                )

                existing_area = (
                    ex2 - ex1
                ) * (
                    ey2 - ey1
                )

                overlap = (
                    intersection_area
                    /
                    min(
                        region_area,
                        existing_area
                    )
                )

                if overlap > 0.50:

                    merged[i] = (
                        min(x1, ex1),
                        min(y1, ey1),
                        max(x2, ex2),
                        max(y2, ey2)
                    )

                    merged_with_existing = True

                    break

        if not merged_with_existing:

            merged.append(
                region
            )

    # -----------------------------------------------------
    # SORT REGIONS
    # -----------------------------------------------------

    merged.sort(
        key=lambda r: (
            r[1],
            r[0]
        )
    )

    return merged[:MAX_DIFFERENCES]


# =========================================================
# DETECT REGIONS ONCE
# =========================================================

if not st.session_state.regions:

    st.session_state.regions = (
        detect_differences(
            img1,
            img2
        )
    )


# =========================================================
# DRAW GREEN TICK
# =========================================================

def draw_found_marks(
    image,
    found_regions
):

    marked_image = image.copy()

    draw = ImageDraw.Draw(
        marked_image
    )

    for index in found_regions:

        if index >= len(
            st.session_state.regions
        ):
            continue

        x1, y1, x2, y2 = (
            st.session_state.regions[index]
        )

        center_x = int(
            (x1 + x2) / 2
        )

        center_y = int(
            (y1 + y2) / 2
        )

        radius = 22

        # Green circle
        draw.ellipse(
            (
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius
            ),
            outline="lime",
            width=5
        )

        # Green tick
        draw.line(
            [
                (
                    center_x - 10,
                    center_y
                ),
                (
                    center_x - 2,
                    center_y + 9
                ),
                (
                    center_x + 13,
                    center_y - 10
                )
            ],
            fill="lime",
            width=6
        )

    return marked_image


# =========================================================
# RESET GAME
# =========================================================

def reset_game():

    st.session_state.game_started = False
    st.session_state.game_paused = False
    st.session_state.game_finished = False

    st.session_state.score = 0
    st.session_state.found_regions = []

    st.session_state.start_time = None
    st.session_state.pause_time = None
    st.session_state.total_paused_time = 0

    st.session_state.message = ""
    st.session_state.message_type = ""


# =========================================================
# START SCREEN
# =========================================================

if not st.session_state.game_started:

    st.markdown(
        '<div class="main-title">'
        '🔎 THE UNSEEN'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'MYSTERY DIFFERENCE CHALLENGE'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="info-box">

        🔎 <b>Find 20 hidden differences</b><br><br>

        Compare both mystery rooms carefully.<br>

        Click on every difference you discover.<br><br>

        ⏱️ You have only <b>60 seconds</b>.

        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "🔎 DIFFERENCES",
            "20"
        )

    with col2:

        st.metric(
            "💯 MAX SCORE",
            "200"
        )

    with col3:

        st.metric(
            "⏱️ TIME",
            "60 SEC"
        )

    st.write("")

    col_left, col_center, col_right = st.columns(
        [1, 2, 1]
    )

    with col_center:

        if st.button(
            "🚪 START MYSTERY",
            use_container_width=True
        ):

            st.session_state.game_started = True
            st.session_state.game_paused = False
            st.session_state.game_finished = False

            st.session_state.score = 0
            st.session_state.found_regions = []

            st.session_state.start_time = time.time()

            st.session_state.pause_time = None
            st.session_state.total_paused_time = 0

            st.session_state.message = ""
            st.session_state.message_type = ""

            st.rerun()

    st.stop()


# =========================================================
# PAUSE SCREEN
# =========================================================

if st.session_state.game_paused:

    st.markdown(
        '<div class="main-title">'
        '⏸️ GAME PAUSED'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'THE MYSTERY IS WAITING'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "⭐ STARS",
            len(
                st.session_state.found_regions
            )
        )

    with col2:

        st.metric(
            "💯 SCORE",
            st.session_state.score
        )

    with col3:

        st.metric(
            "🔎 FOUND",
            f"{len(st.session_state.found_regions)}/{MAX_DIFFERENCES}"
        )

    st.write("")

    col1, col2, col3 = st.columns(
        [1, 2, 1]
    )

    with col2:

        if st.button(
            "▶️ RESUME GAME",
            use_container_width=True
        ):

            if st.session_state.pause_time:

                paused_duration = (
                    time.time()
                    -
                    st.session_state.pause_time
                )

                st.session_state.total_paused_time += (
                    paused_duration
                )

            st.session_state.pause_time = None
            st.session_state.game_paused = False

            st.rerun()

        if st.button(
            "🚪 EXIT GAME",
            use_container_width=True
        ):

            reset_game()

            st.rerun()

    st.stop()


# =========================================================
# FINISHED SCREEN
# =========================================================

if st.session_state.game_finished:

    found = len(
        st.session_state.found_regions
    )

    if found >= MAX_DIFFERENCES:

        st.markdown(
            '<div class="main-title">'
            '🎉 MYSTERY SOLVED!'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="subtitle">'
            'YOU FOUND ALL 20 DIFFERENCES!'
            '</div>',
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            '<div class="main-title">'
            "⏰ TIME'S UP!"
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="subtitle">'
            'THE MYSTERY REMAINS...'
            '</div>',
            unsafe_allow_html=True
        )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "⭐ STARS",
            found
        )

    with col2:

        st.metric(
            "💯 SCORE",
            st.session_state.score
        )

    with col3:

        st.metric(
            "🔎 FOUND",
            f"{found}/{MAX_DIFFERENCES}"
        )

    st.write("")

    col1, col2, col3 = st.columns(
        [1, 2, 1]
    )

    with col2:

        if st.button(
            "🔄 PLAY AGAIN",
            use_container_width=True
        ):

            reset_game()

            st.rerun()

        if st.button(
            "🚪 EXIT GAME",
            use_container_width=True
        ):

            reset_game()

            st.rerun()

    st.stop()


# =========================================================
# GAME AREA
# =========================================================

@st.fragment(run_every=1)
def game_area():

    # -----------------------------------------------------
    # TIMER
    # -----------------------------------------------------

    elapsed = (
        time.time()
        -
        st.session_state.start_time
        -
        st.session_state.total_paused_time
    )

    remaining = max(
        0,
        int(
            TIME_LIMIT
            -
            elapsed
        )
    )

    if remaining <= 0:

        st.session_state.game_finished = True

        st.rerun()

    minutes = remaining // 60
    seconds = remaining % 60

    timer_text = (
        f"{minutes:02d}:{seconds:02d}"
    )


    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    st.markdown(
        '<div class="main-title">'
        '🔎 THE UNSEEN'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'FIND THE HIDDEN DIFFERENCES'
        '</div>',
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # STATS
    # -----------------------------------------------------

    found = len(
        st.session_state.found_regions
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "⭐ STARS",
            found
        )

    with col2:

        st.metric(
            "💯 SCORE",
            st.session_state.score
        )

    with col3:

        st.metric(
            "⏱️ TIME",
            timer_text
        )


    # -----------------------------------------------------
    # PROGRESS
    # -----------------------------------------------------

    progress = min(
        found / MAX_DIFFERENCES,
        1.0
    )

    st.progress(
        progress,
        text=(
            f"🔎 Differences Found: "
            f"{found}/{MAX_DIFFERENCES}"
        )
    )


    # -----------------------------------------------------
    # PAUSE / EXIT
    # -----------------------------------------------------

    col1, col2, col3 = st.columns(
        [1, 1, 1]
    )

    with col1:

        if st.button(
            "⏸️ PAUSE",
            use_container_width=True
        ):

            st.session_state.pause_time = time.time()

            st.session_state.game_paused = True

            st.rerun()

    with col3:

        if st.button(
            "🚪 EXIT GAME",
            use_container_width=True
        ):

            reset_game()

            st.rerun()


    # -----------------------------------------------------
    # MESSAGE
    # -----------------------------------------------------

    if st.session_state.message:

        if (
            st.session_state.message_type
            == "success"
        ):

            st.markdown(
                f"""
                <div class="success-message">
                {st.session_state.message}
                </div>
                """,
                unsafe_allow_html=True
            )

        elif (
            st.session_state.message_type
            == "wrong"
        ):

            st.markdown(
                f"""
                <div class="wrong-message">
                {st.session_state.message}
                </div>
                """,
                unsafe_allow_html=True
            )


    # -----------------------------------------------------
    # IMAGE TITLES
    # -----------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            "<h3 style='text-align:center;'>ROOM A</h3>",
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            "<h3 style='text-align:center;'>ROOM B</h3>",
            unsafe_allow_html=True
        )


    # -----------------------------------------------------
    # ADD GREEN TICKS
    # -----------------------------------------------------

    marked_img1 = draw_found_marks(
        img1,
        st.session_state.found_regions
    )

    marked_img2 = draw_found_marks(
        img2,
        st.session_state.found_regions
    )


    # -----------------------------------------------------
    # CLICKABLE IMAGES
    # -----------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        click1 = streamlit_image_coordinates(
            marked_img1,
            key="image_1"
        )

    with col2:

        click2 = streamlit_image_coordinates(
            marked_img2,
            key="image_2"
        )


    # -----------------------------------------------------
    # GET CLICK
    # -----------------------------------------------------

    click = None

    if click1 is not None:

        click = click1

    elif click2 is not None:

        click = click2

    if click is None:

        return


    click_x = click["x"]
    click_y = click["y"]


    # -----------------------------------------------------
    # FIND MATCHING REGION
    # -----------------------------------------------------

    tolerance = 35

    clicked_region = None

    for index, region in enumerate(
        st.session_state.regions
    ):

        x1, y1, x2, y2 = region

        if (
            x1 - tolerance
            <= click_x
            <= x2 + tolerance
            and
            y1 - tolerance
            <= click_y
            <= y2 + tolerance
        ):

            clicked_region = index

            break


    # -----------------------------------------------------
    # CORRECT DIFFERENCE
    # -----------------------------------------------------

    if clicked_region is not None:

        # Already found = do absolutely nothing
        if (
            clicked_region
            in st.session_state.found_regions
        ):

            return


        # Add found difference
        st.session_state.found_regions.append(
            clicked_region
        )

        # Add score
        st.session_state.score += (
            POINTS_PER_DIFFERENCE
        )

        # Success message
        st.session_state.message = (
            "⭐ CORRECT! +1 STAR +10 POINTS"
        )

        st.session_state.message_type = (
            "success"
        )


        # All differences found
        if len(
            st.session_state.found_regions
        ) >= MAX_DIFFERENCES:

            st.session_state.game_finished = True

            st.rerun()


        st.rerun()


    # -----------------------------------------------------
    # WRONG CLICK
    # -----------------------------------------------------

    st.session_state.message = (
        "❌ NOT A DIFFERENCE! Try again 🔎"
    )

    st.session_state.message_type = (
        "wrong"
    )

    st.rerun()


# =========================================================
# RUN GAME
# =========================================================

game_area()


# =========================================================
# INSTRUCTIONS
# =========================================================

st.markdown("---")

st.markdown(
    """
    <div class="info-box">

    🔎 <b>HOW TO PLAY</b><br><br>

    Compare Room A and Room B carefully.<br>

    Click on anything that looks different.<br><br>

    ⭐ Correct difference = +1 Star<br>

    💯 Correct difference = +10 Points<br>

    ⏱️ Find all 20 before the timer ends.<br><br>

    ✅ Found differences will be marked with a green tick.

    </div>
    """,
    unsafe_allow_html=True
)