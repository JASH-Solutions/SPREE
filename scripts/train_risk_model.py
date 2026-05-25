from app.utils.model_persistence import train_and_persist_risk_model


if __name__ == "__main__":
    artifact = train_and_persist_risk_model()
    print(f"Modelo guardado en: {artifact['model_path']}")
    print(f"Metadata guardada en: {artifact['metadata_path']}")
