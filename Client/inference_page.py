import io
import time
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import requests
import librosa
from streamlit_mic_recorder import mic_recorder

ADVICE_MAP = {
    "р": "Попробуйте упражнение «Моторчик»: длительно произносите «д-д-д-д-р-р-р». Язык вибрирует у нёба.",
    "л": "Улыбнитесь, прикусите кончик языка и произнесите «ллл». Язык упирается в верхние зубы.",
    "ш": "Сделайте «чашечку» языком и подуйте на кончик носа – получится «шшш». Губы округлены.",
    "щ": "Язык поднят к нёбу, произносите мягко «щщщ» – как будто шипит змея.",
    "ц": "Быстро произнесите «т-с» слитно: «ц». Кончик языка упирается в нижние зубы.",
    "ч": "Язык прижат к нёбу, резко отрывается – получается «ч». Как «ть-щ» слитно.",
    "т": "Кончик языка стучит по верхним зубам: «т-т-т». Следите, чтобы не было «ть».",
    "с": "Улыбнитесь, язык «желобком», подуйте – получится «с-с-с». Зубы сомкнуты.",
}

TWISTERS_DATA = {
    "рлш": {
        "text": "Наш голова вашего голову головой переголовил, перевыголовил",
        "sounds": ["р", "л", "ш"]
    },
    "стр": {
        "text": "Хитрую сороку поймать морока, а сорок сорок — сорок морок",
        "sounds": ["с", "т", "р"]
    },
    "трш": {
        "text": "Шарики шарикоподшипника шарят по подшипнику",
        "sounds": ["т", "р", "ш"]
    },
    "стрлш": {
        "text": "Токарь Раппопорт пропил пропуск, рашпиль и суппорт",
        "sounds": ["с", "т", "р", "л", "ш"]
    },
    "чстрл": {
        "text": "Четыре чёрненьких чумазеньких чертёнка чертили чёрными чернилами чертёж чрезвычайно чисто",
        "sounds": ["ч", "с", "т", "р", "л"]
    }
}


def validate_audio(file_bytes: bytes, min_duration=0.5, max_duration=30.0):
    """Проверяет аудиофайл: пустой? слишком короткий/длинный? можно ли загрузить?"""
    if not file_bytes or len(file_bytes) == 0:
        return False, "Файл пуст. Пожалуйста, загрузите или запишите аудио."
    try:
        y, sr = librosa.load(io.BytesIO(file_bytes), sr=16000)
        duration = len(y) / sr
        if duration < min_duration:
            return False, f"Аудио слишком короткое ({duration:.2f} сек). Минимальная длительность – {min_duration} сек."
        if duration > max_duration:
            return False, f"Аудио слишком длинное ({duration:.2f} сек). Максимальная длительность – {max_duration} сек."
        return True, duration
    except Exception as e:
        return False, f"Не удалось прочитать аудиофайл. Причина: {str(e)}"
    

def plot_oscillogram(file_bytes: bytes, title="Осциллограмма"):
    """Строит осциллограмму (амплитуда vs время)"""
    y, sr = librosa.load(io.BytesIO(file_bytes), sr=16000)
    duration = len(y) / sr
    time_axis = np.linspace(0, duration, len(y))
    
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(time_axis, y, linewidth=0.8, color='steelblue')
    ax.set_xlabel('Время (с)')
    ax.set_ylabel('Амплитуда')
    ax.set_title(title)
    ax.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig)
    plt.close(fig)
    return duration


def inference_page(backend_url: str):
    st.header("Проверка произношения скороговорки")
    
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    with st.sidebar:
        st.subheader("📜 История проверок")
        if st.session_state.history:
            for i, rec in enumerate(reversed(st.session_state.history[-10:])):
                st.write(f"**{rec['timestamp']}** – {rec['twister']}")
                st.write(f"Результат: {rec['prediction']} ({rec['probability']:.1%})")
                if rec.get('problematic'):
                    st.write(f"⚠️ {', '.join(rec['problematic'])}")
                st.divider()
        else:
            st.info("Пока нет проверок. Загрузите или запишите аудио и нажмите кнопку.")
        
        st.divider()
        st.subheader("📖 Словарь советов для звуков")
        for sound, advice in sorted(ADVICE_MAP.items()):
            with st.expander(f"Звук **{sound}**"):
                st.write(advice)
    
    selected_type = st.selectbox(
        "Выберите скороговорку",
        list(TWISTERS_DATA.keys()),
        format_func=lambda x: f"{x} – {TWISTERS_DATA[x]['text'][:60]}..."
    )
    st.info(f"**Текст скороговорки:**\n\n{TWISTERS_DATA[selected_type]['text']}")
    sounds_str = ", ".join(TWISTERS_DATA[selected_type]["sounds"])
    st.caption(f"🔍 Эта скороговорка проверяет звуки: **{sounds_str}**")
    
    input_method = st.radio("Как вы хотите предоставить аудио?", ["🎙️ Записать через микрофон", "📁 Загрузить файл"])
    
    audio_bytes = None
    valid = False
    error_msg = None

    if input_method == "🎙️ Записать через микрофон":
        recorded = mic_recorder(start_prompt="Начать запись", stop_prompt="Остановить запись", format="wav")
        if recorded:
            audio_bytes = recorded['bytes']
            ok, msg = validate_audio(audio_bytes)
            if ok:
                valid = True
                duration = msg
                st.audio(audio_bytes, format='audio/wav')
                st.caption(f"✅ Длительность: {duration:.2f} сек")
                plot_oscillogram(audio_bytes, title="Записанная осциллограмма")
            else:
                st.error(msg)
                valid = False
                audio_bytes = None
    else:
        uploaded_file = st.file_uploader("Аудиофайл", type=["wav", "mp3", "ogg"])
        if uploaded_file is not None:
            audio_bytes = uploaded_file.getvalue()
            st.audio(audio_bytes, format='audio/wav')
            ok, msg = validate_audio(audio_bytes)
            if ok:
                valid = True
                duration = msg
                st.caption(f"✅ Длительность: {duration:.2f} сек")
                plot_oscillogram(audio_bytes, title="Осциллограмма загруженного файла")
            else:
                st.error(msg)
                valid = False
                audio_bytes = None
    
    if audio_bytes and valid and st.button("Определить дефекты речи"):
        with st.spinner("Анализируем произношение... Подождите секунду"):
            files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
            data = {"twister": selected_type}
            try:
                resp = requests.post(f"{backend_url}/predict", files=files, data=data, timeout=30)
                if resp.status_code == 200:
                    result = resp.json()
                    prediction = result["prediction"]
                    probability = result["probability"]
                    problematic = result.get("problematic_sounds", [])
                    
                    if prediction == "хорошо":
                        st.success(f"✅ **Результат:** {prediction} (вероятность дефекта: {probability:.2%})")
                        st.balloons()
                    else:
                        st.error(f"❌ **Результат:** {prediction} (вероятность дефекта: {probability:.2%})")
                        if problematic:
                            st.warning(f"⚠️ Возможные проблемные звуки: **{', '.join(problematic)}**")
                            for sound in problematic:
                                if sound in ADVICE_MAP:
                                    st.info(f"💡 **Совет для звука «{sound}»:** {ADVICE_MAP[sound]}")
                        else:
                            st.info("Проблемные звуки не определены автоматически. Обратитесь к логопеду.")
                    
                    st.session_state.history.append({
                        "timestamp": time.strftime("%H:%M:%S"),
                        "twister": selected_type,
                        "prediction": prediction,
                        "probability": probability,
                        "problematic": problematic
                    })
                elif resp.status_code == 400:
                    st.error(f"Ошибка в запросе: {resp.json().get('detail', 'Некорректные данные')}")
                elif resp.status_code == 413:
                    st.error("Файл слишком большой. Пожалуйста, загрузите файл меньшего размера.")
                else:
                    st.error(f"Ошибка сервера: {resp.text}")
            except requests.exceptions.Timeout:
                st.error("Превышено время ожидания ответа от сервера. Попробуйте ещё раз.")
            except Exception as e:
                st.error(f"Не удалось соединиться с сервером: {e}")