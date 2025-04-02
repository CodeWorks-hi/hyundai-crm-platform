import streamlit as st



def render_carousel(car_data: list, height: int = 400):
    names = [car["name"] for car in car_data]

    carousel_html = f"""
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper/swiper-bundle.min.css">
    <script src="https://cdn.jsdelivr.net/npm/swiper/swiper-bundle.min.js"></script>

    <style>
    .swiper-container {{
        width: 100%;
        height: {height - 40}px;
        position: relative;
    }}
    .swiper-slide img {{
        width: 100%;
        height: {height - 100}px;
        object-fit: contain;
        border-radius: 10px;
    }}
    .nav-label {{
        position: absolute;
        top: 50%;
        font-size: 14px;
        color: #000;
        z-index: 10;
        transform: translateY(-50%);
        pointer-events: none;
        font-weight: bold;
    }}
    .prev-label {{ left: 30px; }}
    .next-label {{ right: 30px; }}
    </style>

    <div class="swiper-container">
        <div class="swiper-wrapper">
            {''.join(f'<div class="swiper-slide" data-name="{car["name"]}"><img src="{car["url"]}" alt="{car["name"]}"></div>' for car in car_data)}
        </div>
        <div class="swiper-button-next"></div>
        <div class="swiper-button-prev"></div>
        <div class="swiper-pagination"></div>
        <div class="nav-label prev-label" id="prevName"></div>
        <div class="nav-label next-label" id="nextName"></div>
    </div>

    <script>
        const names = {names};

        const swiper = new Swiper('.swiper-container', {{
            loop: true,
            autoplay: {{
                delay: 3000,
                disableOnInteraction: false
            }},
            navigation: {{
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev'
            }},
            pagination: {{
                el: '.swiper-pagination',
                clickable: true
            }},
            on: {{
                slideChange: function () {{
                    const total = names.length;
                    const realIndex = this.realIndex;
                    const prevName = names[(realIndex - 1 + total) % total];
                    const nextName = names[(realIndex + 1) % total];
                    document.getElementById("prevName").textContent = prevName;
                    document.getElementById("nextName").textContent = nextName;
                }}
            }}
        }});

        window.addEventListener('DOMContentLoaded', () => {{
            swiper.emit('slideChange');
        }});
    </script>
    """

    st.components.v1.html(carousel_html, height=height)