import io
import numpy as np
import librosa

TARGET_SR = 16000
MAX_LEN = 10 * TARGET_SR


def load_audio(file_bytes: bytes) -> np.ndarray:
    """Загружает аудио из байтов, приводит к 16 кГц и 10 секундам"""
    y, sr = librosa.load(io.BytesIO(file_bytes), sr=TARGET_SR)
    if len(y) > MAX_LEN:
        start = (len(y) - MAX_LEN) // 2
        y = y[start:start+MAX_LEN]
    else:
        pad_len = MAX_LEN - len(y)
        y = np.pad(y, (pad_len//2, pad_len - pad_len//2), mode='constant')
    return y


def extract_mfcc_features(y: np.ndarray) -> np.ndarray:
    """Извлекает 255 MFCC-признаков"""
    mfcc = librosa.feature.mfcc(y=y, sr=TARGET_SR, n_mfcc=40)
    mfcc_mean = np.mean(mfcc, axis=1)
    mfcc_std = np.std(mfcc, axis=1)
    
    mfcc_delta = librosa.feature.delta(mfcc)
    mfcc_delta2 = librosa.feature.delta(mfcc, order=2)
    delta_mean = np.mean(mfcc_delta, axis=1)
    delta_std = np.std(mfcc_delta, axis=1)
    delta2_mean = np.mean(mfcc_delta2, axis=1)
    delta2_std = np.std(mfcc_delta2, axis=1)
    
    cent = librosa.feature.spectral_centroid(y=y, sr=TARGET_SR)
    cent_mean, cent_std = np.mean(cent), np.std(cent)
    bw = librosa.feature.spectral_bandwidth(y=y, sr=TARGET_SR)
    bw_mean, bw_std = np.mean(bw), np.std(bw)
    contrast = librosa.feature.spectral_contrast(y=y, sr=TARGET_SR)
    contrast_mean = np.mean(contrast, axis=1)
    zcr = librosa.feature.zero_crossing_rate(y)
    zcr_mean, zcr_std = np.mean(zcr), np.std(zcr)
    rms = librosa.feature.rms(y=y)
    rms_mean, rms_std = np.mean(rms), np.std(rms)
    
    features = np.concatenate([
        mfcc_mean, mfcc_std,
        delta_mean, delta_std,
        delta2_mean, delta2_std,
        [cent_mean, cent_std, bw_mean, bw_std],
        contrast_mean,
        [zcr_mean, zcr_std, rms_mean, rms_std]
    ])
    return features


def preprocess_audio(file_bytes: bytes) -> np.ndarray:
    """Полный пайплайн: загрузка аудио → извлечение MFCC."""
    y = load_audio(file_bytes)
    features = extract_mfcc_features(y)
    return features