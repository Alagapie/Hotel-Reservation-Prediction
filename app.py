import joblib
import pandas as pd
from flask import Flask, render_template, request

from config.paths_config import CONFIG_PATH, MODEL_OUTPUT_PATH, TRAIN_FILE_PATH
from utils.common_functions import read_yaml

PREPROCESSOR_PATH = "artifacts/preprocessor.pkl"
LABEL_ENCODER_PATH = "artifacts/label_encoder.pkl"

app = Flask(__name__, template_folder="template", static_folder="static")

config = read_yaml(CONFIG_PATH)
NUMERICAL_COLUMNS = config["data_processing"]["numerical_columns"]
CATEGORICAL_COLUMNS = config["data_processing"]["categorical_columns"]
FEATURE_COLUMNS = NUMERICAL_COLUMNS + CATEGORICAL_COLUMNS

model = None
preprocessor = None
label_encoder = None
load_error = None
CATEGORICAL_OPTIONS = {}
NUMERIC_STATS = {}
INTEGER_COLUMNS = {
    "no_of_adults",
    "no_of_children",
    "no_of_weekend_nights",
    "no_of_week_nights",
    "required_car_parking_space",
    "lead_time",
    "arrival_year",
    "arrival_month",
    "arrival_date",
    "repeated_guest",
    "no_of_previous_cancellations",
    "no_of_previous_bookings_not_canceled",
    "no_of_special_requests",
}
FIELD_LABELS = {
    "no_of_adults": "Number of Adults",
    "no_of_children": "Number of Children",
    "no_of_weekend_nights": "Weekend Nights",
    "no_of_week_nights": "Week Nights",
    "required_car_parking_space": "Car Parking Required",
    "lead_time": "Lead Time (Days)",
    "arrival_year": "Arrival Year",
    "arrival_month": "Arrival Month",
    "arrival_date": "Arrival Date",
    "repeated_guest": "Repeated Guest",
    "no_of_previous_cancellations": "Previous Cancellations",
    "no_of_previous_bookings_not_canceled": "Previous Non-Canceled Bookings",
    "avg_price_per_room": "Average Price Per Room",
    "no_of_special_requests": "Special Requests",
    "type_of_meal_plan": "Meal Plan",
    "room_type_reserved": "Room Type Reserved",
    "market_segment_type": "Market Segment",
}
FIELD_HELPERS = {
    "lead_time": "Days between booking and arrival.",
    "avg_price_per_room": "Average room price for the stay.",
    "required_car_parking_space": "Whether parking is requested.",
    "repeated_guest": "Has the guest stayed before.",
}
BINARY_COLUMNS = {"required_car_parking_space", "repeated_guest"}
MONTH_OPTIONS = [
    {"value": 1, "label": "January"},
    {"value": 2, "label": "February"},
    {"value": 3, "label": "March"},
    {"value": 4, "label": "April"},
    {"value": 5, "label": "May"},
    {"value": 6, "label": "June"},
    {"value": 7, "label": "July"},
    {"value": 8, "label": "August"},
    {"value": 9, "label": "September"},
    {"value": 10, "label": "October"},
    {"value": 11, "label": "November"},
    {"value": 12, "label": "December"},
]

def _ensure_artifacts_loaded():
    global model, preprocessor, label_encoder, load_error
    if model is not None and preprocessor is not None and label_encoder is not None:
        return
    try:
        model = joblib.load(MODEL_OUTPUT_PATH)
        preprocessor = joblib.load(PREPROCESSOR_PATH)
        label_encoder = joblib.load(LABEL_ENCODER_PATH)
        load_error = None
    except Exception as exc:
        load_error = str(exc)


def _ensure_feature_metadata_loaded():
    global CATEGORICAL_OPTIONS, NUMERIC_STATS
    if CATEGORICAL_OPTIONS and NUMERIC_STATS:
        return

    try:
        df = pd.read_csv(TRAIN_FILE_PATH, usecols=FEATURE_COLUMNS)
        for col in CATEGORICAL_COLUMNS:
            values = df[col].dropna().astype(str).str.strip().unique().tolist()
            CATEGORICAL_OPTIONS[col] = sorted([v for v in values if v])

        for col in NUMERICAL_COLUMNS:
            series = pd.to_numeric(df[col], errors="coerce").dropna()
            NUMERIC_STATS[col] = {
                "min": float(series.min()),
                "max": float(series.max()),
                "mean": round(float(series.mean()), 2),
                "step": 1 if col in INTEGER_COLUMNS else 0.01,
                "is_int": col in INTEGER_COLUMNS,
            }
    except Exception:
        for col in CATEGORICAL_COLUMNS:
            CATEGORICAL_OPTIONS.setdefault(col, [])
        for col in NUMERICAL_COLUMNS:
            NUMERIC_STATS.setdefault(
                col,
                {"min": None, "max": None, "mean": None, "step": "any", "is_int": False},
            )


def _build_input_dataframe(form_data):
    row = {}

    for col in NUMERICAL_COLUMNS:
        value = form_data.get(col, "").strip()
        if value == "":
            raise ValueError(f"Missing value for {col}")
        parsed = float(value)
        row[col] = int(parsed) if col in INTEGER_COLUMNS else parsed

    for col in CATEGORICAL_COLUMNS:
        value = form_data.get(col, "").strip()
        if value == "":
            raise ValueError(f"Missing value for {col}")
        row[col] = value

    return pd.DataFrame([row], columns=FEATURE_COLUMNS)


@app.route("/", methods=["GET", "POST"])
def home():
    prediction = None
    confidence = None
    error = None
    _ensure_feature_metadata_loaded()
    year_options = []
    if num_stats := NUMERIC_STATS.get("arrival_year"):
        if num_stats.get("min") is not None and num_stats.get("max") is not None:
            year_options = list(
                range(int(num_stats["min"]), int(num_stats["max"]) + 1)
            )

    if request.method == "POST":
        _ensure_artifacts_loaded()
        if load_error:
            error = (
                "Model artifacts could not be loaded. "
                f"Check files and paths. Details: {load_error}"
            )
        else:
            try:
                input_df = _build_input_dataframe(request.form)
                transformed = preprocessor.transform(input_df)

                pred_encoded = model.predict(transformed)[0]
                prediction = label_encoder.inverse_transform([int(pred_encoded)])[0]

                if hasattr(model, "predict_proba"):
                    proba = model.predict_proba(transformed)[0]
                    confidence = round(float(max(proba)) * 100, 2)
            except Exception as exc:
                error = str(exc)

    return render_template(
        "index.html",
        num_cols=NUMERICAL_COLUMNS,
        cat_cols=CATEGORICAL_COLUMNS,
        cat_options=CATEGORICAL_OPTIONS,
        num_stats=NUMERIC_STATS,
        field_labels=FIELD_LABELS,
        field_helpers=FIELD_HELPERS,
        binary_cols=BINARY_COLUMNS,
        month_options=MONTH_OPTIONS,
        year_options=year_options,
        prediction=prediction,
        confidence=confidence,
        error=error,
        load_error=load_error,
    )


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 80))  # Azure provides PORT
    app.run(host="0.0.0.0", port=port)
