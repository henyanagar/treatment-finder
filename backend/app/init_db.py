from app.core.database import create_db_and_tables
from sqlmodel import Session, select

from app.core.database import engine
from app.models import Clinic, ClinicServiceLink, Service, TreatmentCategory


def seed_initial_data() -> None:
    with Session(engine) as session:
        categories_seed = {
            "Injectables": "Injectable aesthetic procedures such as botulinum toxin and dermal fillers.",
            "Skin Treatments": "Medical skin treatments for texture, pigmentation, and skin health.",
            "Laser / Device Treatments": "Technology-based treatments using laser, RF, IPL, or cooling devices.",
            "Surgical Consultations": "Consultations and planning for elective surgical aesthetic procedures.",
            "Dental Aesthetics": "Aesthetic and preventive oral treatments for smile enhancement.",
            "Physiotherapy": "Movement rehabilitation and musculoskeletal recovery treatments.",
            "Hair & Scalp Treatments": "Hair restoration and scalp-focused treatment options.",
            "Wellness & Recovery": "Recovery, preventive, and wellness-focused supportive treatments.",
        }

        for category_name, category_description in categories_seed.items():
            category = session.exec(
                select(TreatmentCategory).where(TreatmentCategory.name == category_name)
            ).first()
            if not category:
                session.add(TreatmentCategory(name=category_name, description=category_description))
            else:
                category.description = category_description

        session.commit()
        categories_by_name = {
            category.name: category.id for category in session.exec(select(TreatmentCategory)).all()
        }

        services_seed = [
            {
                "name": "Botox Injection",
                "category": "Injectables",
                "description": "Botulinum toxin treatment that relaxes targeted facial muscles to reduce dynamic wrinkles.",
                "treatment_type": "injectable",
                "invasiveness_level": "minimally_invasive",
                "is_technology_based": False,
                "recovery_level": "low",
            },
            {
                "name": "Hyaluronic Acid Filler",
                "category": "Injectables",
                "description": "Dermal filler treatment that restores volume and contour by hydrating deep skin layers.",
                "treatment_type": "injectable",
                "invasiveness_level": "minimally_invasive",
                "is_technology_based": False,
                "recovery_level": "low",
            },
            {
                "name": "Hyperhidrosis Botox Treatment",
                "category": "Injectables",
                "description": "Targeted botulinum injections that reduce excessive sweating by blocking sweat-gland signaling.",
                "treatment_type": "injectable",
                "invasiveness_level": "minimally_invasive",
                "is_technology_based": False,
                "recovery_level": "low",
            },
            {
                "name": "Dermatology Consultation",
                "category": "Skin Treatments",
                "description": "Clinical skin consultation for acne, dryness, sensitivity, and chronic skin conditions.",
                "treatment_type": "medical_consultation",
                "invasiveness_level": "non_invasive",
                "is_technology_based": False,
                "recovery_level": "none",
            },
            {
                "name": "Mole Removal",
                "category": "Skin Treatments",
                "description": "Minor medical procedure to remove benign skin lesions for diagnostic or cosmetic indications.",
                "treatment_type": "minor_procedure",
                "invasiveness_level": "minimally_invasive",
                "is_technology_based": True,
                "recovery_level": "medium",
            },
            {
                "name": "CO2 Laser Resurfacing",
                "category": "Laser / Device Treatments",
                "description": "Fractional CO2 laser treatment that stimulates collagen to improve scars, texture, and fine lines.",
                "treatment_type": "laser",
                "invasiveness_level": "minimally_invasive",
                "is_technology_based": True,
                "recovery_level": "medium",
            },
            {
                "name": "IPL Photorejuvenation",
                "category": "Laser / Device Treatments",
                "description": "Intense Pulsed Light therapy for pigmentation, redness, and uneven skin tone.",
                "treatment_type": "light_device",
                "invasiveness_level": "non_invasive",
                "is_technology_based": True,
                "recovery_level": "low",
            },
            {
                "name": "Cryolipolysis",
                "category": "Laser / Device Treatments",
                "description": "Localized fat freezing treatment that gradually reduces fat cells in targeted body areas.",
                "treatment_type": "body_contouring_device",
                "invasiveness_level": "non_invasive",
                "is_technology_based": True,
                "recovery_level": "low",
            },
            {
                "name": "CoolSculpting",
                "category": "Laser / Device Treatments",
                "description": "Non-invasive cryolipolysis body contouring for stubborn fat pockets.",
                "treatment_type": "body_contouring_device",
                "invasiveness_level": "non_invasive",
                "is_technology_based": True,
                "recovery_level": "low",
            },
            {
                "name": "RF Skin Tightening",
                "category": "Laser / Device Treatments",
                "description": "Radiofrequency treatment that heats dermal tissue to promote collagen remodeling and firm skin.",
                "treatment_type": "rf_device",
                "invasiveness_level": "non_invasive",
                "is_technology_based": True,
                "recovery_level": "low",
            },
            {
                "name": "Rhinoplasty Consultation",
                "category": "Surgical Consultations",
                "description": "Specialist consultation for nasal reshaping options, expectations, and pre-surgical planning.",
                "treatment_type": "surgical_consultation",
                "invasiveness_level": "surgical",
                "is_technology_based": False,
                "recovery_level": "high",
            },
            {
                "name": "Surgical Facial Rejuvenation Consultation",
                "category": "Surgical Consultations",
                "description": "Consultation for facelift or related surgical rejuvenation approaches and candidacy.",
                "treatment_type": "surgical_consultation",
                "invasiveness_level": "surgical",
                "is_technology_based": False,
                "recovery_level": "high",
            },
            {
                "name": "Dental Cleaning",
                "category": "Dental Aesthetics",
                "description": "Professional preventive cleaning to remove plaque and tartar and improve smile appearance.",
                "treatment_type": "dental_preventive",
                "invasiveness_level": "non_invasive",
                "is_technology_based": True,
                "recovery_level": "none",
            },
            {
                "name": "Teeth Whitening",
                "category": "Dental Aesthetics",
                "description": "Aesthetic whitening procedure to brighten enamel and improve smile color tone.",
                "treatment_type": "dental_aesthetic",
                "invasiveness_level": "non_invasive",
                "is_technology_based": True,
                "recovery_level": "none",
            },
            {
                "name": "Physiotherapy",
                "category": "Physiotherapy",
                "description": "Guided movement rehabilitation for orthopedic pain, mobility limits, and post-injury recovery.",
                "treatment_type": "rehabilitation",
                "invasiveness_level": "non_invasive",
                "is_technology_based": False,
                "recovery_level": "low",
            },
            {
                "name": "Sports Injury Rehabilitation",
                "category": "Physiotherapy",
                "description": "Structured rehab program for return-to-activity after sprain, strain, or overuse injuries.",
                "treatment_type": "rehabilitation",
                "invasiveness_level": "non_invasive",
                "is_technology_based": False,
                "recovery_level": "medium",
            },
            {
                "name": "Hair Restoration Consultation",
                "category": "Hair & Scalp Treatments",
                "description": "Clinical assessment of hair thinning and loss with treatment planning options.",
                "treatment_type": "medical_consultation",
                "invasiveness_level": "non_invasive",
                "is_technology_based": False,
                "recovery_level": "none",
            },
            {
                "name": "Scalp Therapy Session",
                "category": "Hair & Scalp Treatments",
                "description": "Targeted scalp treatment to support scalp barrier health and improve follicle environment.",
                "treatment_type": "scalp_therapy",
                "invasiveness_level": "non_invasive",
                "is_technology_based": True,
                "recovery_level": "none",
            },
            {
                "name": "Sports Massage",
                "category": "Wellness & Recovery",
                "description": "Manual recovery treatment to reduce muscle tension and support post-activity recovery.",
                "treatment_type": "wellness_manual",
                "invasiveness_level": "non_invasive",
                "is_technology_based": False,
                "recovery_level": "low",
            },
            {
                "name": "Nutrition Consultation",
                "category": "Wellness & Recovery",
                "description": "Personalized dietary assessment and plan for metabolic support and recovery goals.",
                "treatment_type": "wellness_consultation",
                "invasiveness_level": "non_invasive",
                "is_technology_based": False,
                "recovery_level": "none",
            },
            {
                "name": "General Checkup",
                "category": "Wellness & Recovery",
                "description": "Routine preventive health check with baseline indicators and recommendations.",
                "treatment_type": "medical_checkup",
                "invasiveness_level": "non_invasive",
                "is_technology_based": False,
                "recovery_level": "none",
            },
            {
                "name": "Lymphatic Drainage Therapy",
                "category": "Wellness & Recovery",
                "description": "Recovery-oriented therapy that supports fluid movement and post-procedure swelling reduction.",
                "treatment_type": "wellness_manual",
                "invasiveness_level": "non_invasive",
                "is_technology_based": False,
                "recovery_level": "low",
            },
            {
                "name": "Micro-needling",
                "category": "Laser / Device Treatments",
                "description": "Collagen induction treatment that uses controlled micro-injuries to improve texture and scars.",
                "treatment_type": "needling_device",
                "invasiveness_level": "minimally_invasive",
                "is_technology_based": True,
                "recovery_level": "low",
            },
        ]

        for item in services_seed:
            service = session.exec(select(Service).where(Service.name == item["name"])).first()
            if not service:
                session.add(
                    Service(
                        name=item["name"],
                        description=item["description"],
                        category_id=categories_by_name[item["category"]],
                        treatment_type=item["treatment_type"],
                        invasiveness_level=item["invasiveness_level"],
                        is_technology_based=item["is_technology_based"],
                        recovery_level=item["recovery_level"],
                    )
                )
            else:
                service.description = item["description"]
                service.category_id = categories_by_name[item["category"]]
                service.treatment_type = item["treatment_type"]
                service.invasiveness_level = item["invasiveness_level"]
                service.is_technology_based = item["is_technology_based"]
                service.recovery_level = item["recovery_level"]

        clinics_seed = [
            Clinic(
                name="City Clinic",
                address="1 Main St",
                city="Tel Aviv",
                latitude=32.0853,
                longitude=34.7818,
                rating=4.7,
            ),
            Clinic(
                name="North Care Center",
                address="10 Oak Rd",
                city="Haifa",
                latitude=32.7940,
                longitude=34.9896,
                rating=4.5,
            ),
            Clinic(
                name="Jerusalem Wellness Hub",
                address="22 Palm Ave",
                city="Jerusalem",
                latitude=31.7683,
                longitude=35.2137,
                rating=4.6,
            ),
            Clinic(
                name="Coastal Family Clinic",
                address="7 Sea View Blvd",
                city="Netanya",
                latitude=32.3215,
                longitude=34.8532,
                rating=4.3,
            ),
            Clinic(
                name="South Health Point",
                address="15 Desert St",
                city="Beersheba",
                latitude=31.2518,
                longitude=34.7913,
                rating=4.4,
            ),
            Clinic(
                name="Nova Medical Aesthetic Center",
                address="120 Innovation Ave",
                city="Tel Aviv",
                latitude=32.0932,
                longitude=34.8015,
                rating=4.8,
            ),
            Clinic(
                name="Elite Laser & Aesthetics Institute",
                address="44 Carmel Tech Park",
                city="Haifa",
                latitude=32.8077,
                longitude=34.9931,
                rating=4.9,
            ),
        ]

        for clinic_seed in clinics_seed:
            clinic = session.exec(select(Clinic).where(Clinic.name == clinic_seed.name)).first()
            if not clinic:
                session.add(clinic_seed)

        session.commit()

        services_by_name = {service.name: service.id for service in session.exec(select(Service)).all()}
        clinics_by_name = {clinic.name: clinic.id for clinic in session.exec(select(Clinic)).all()}

        clinic_service_pairs = [
            ("City Clinic", "Physiotherapy", 260.0, True),
            ("City Clinic", "Dermatology Consultation", 320.0, True),
            ("City Clinic", "General Checkup", 180.0, True),
            ("North Care Center", "Dental Cleaning", 240.0, True),
            ("North Care Center", "General Checkup", 170.0, True),
            ("Jerusalem Wellness Hub", "Nutrition Consultation", 290.0, True),
            ("Jerusalem Wellness Hub", "Dermatology Consultation", 340.0, True),
            ("Coastal Family Clinic", "Sports Massage", 230.0, True),
            ("Coastal Family Clinic", "Physiotherapy", 250.0, True),
            ("Coastal Family Clinic", "Sports Injury Rehabilitation", 280.0, True),
            ("South Health Point", "General Checkup", 160.0, True),
            ("South Health Point", "Nutrition Consultation", 270.0, True),
            ("South Health Point", "Dental Cleaning", 220.0, False),
            ("South Health Point", "Lymphatic Drainage Therapy", 260.0, True),
            ("Nova Medical Aesthetic Center", "Botox Injection", 900.0, True),
            ("Nova Medical Aesthetic Center", "Hyaluronic Acid Filler", 1300.0, True),
            ("Nova Medical Aesthetic Center", "CO2 Laser Resurfacing", 2100.0, True),
            ("Nova Medical Aesthetic Center", "CoolSculpting", 1800.0, True),
            ("Nova Medical Aesthetic Center", "Cryolipolysis", 1850.0, True),
            ("Nova Medical Aesthetic Center", "IPL Photorejuvenation", 1250.0, True),
            ("Nova Medical Aesthetic Center", "Micro-needling", 980.0, True),
            ("Nova Medical Aesthetic Center", "Hyperhidrosis Botox Treatment", 1200.0, True),
            ("Nova Medical Aesthetic Center", "RF Skin Tightening", 1500.0, True),
            ("Nova Medical Aesthetic Center", "Hair Restoration Consultation", 450.0, True),
            ("Elite Laser & Aesthetics Institute", "Botox Injection", 950.0, True),
            ("Elite Laser & Aesthetics Institute", "Rhinoplasty Consultation", 16500.0, True),
            ("Elite Laser & Aesthetics Institute", "Surgical Facial Rejuvenation Consultation", 18000.0, True),
            ("Elite Laser & Aesthetics Institute", "CO2 Laser Resurfacing", 2250.0, True),
            ("Elite Laser & Aesthetics Institute", "CoolSculpting", 1900.0, False),
            ("Elite Laser & Aesthetics Institute", "Hyaluronic Acid Filler", 1450.0, True),
            ("Elite Laser & Aesthetics Institute", "Cryolipolysis", 1920.0, True),
            ("Elite Laser & Aesthetics Institute", "IPL Photorejuvenation", 1300.0, True),
            ("Elite Laser & Aesthetics Institute", "Micro-needling", 1050.0, True),
            ("Elite Laser & Aesthetics Institute", "Mole Removal", 850.0, True),
            ("Elite Laser & Aesthetics Institute", "Scalp Therapy Session", 700.0, True),
            ("Elite Laser & Aesthetics Institute", "Teeth Whitening", 980.0, True),
        ]

        for clinic_name, service_name, price, is_available in clinic_service_pairs:
            clinic_id = clinics_by_name.get(clinic_name)
            service_id = services_by_name.get(service_name)
            if not clinic_id or not service_id:
                continue
            existing_link = session.exec(
                select(ClinicServiceLink).where(
                    ClinicServiceLink.clinic_id == clinic_id,
                    ClinicServiceLink.service_id == service_id,
                )
            ).first()
            if not existing_link:
                session.add(
                    ClinicServiceLink(
                        clinic_id=clinic_id,
                        service_id=service_id,
                        price=price,
                        is_available=is_available,
                    )
                )
            else:
                existing_link.price = price
                existing_link.is_available = is_available

        session.commit()


def init() -> None:
    create_db_and_tables()
    seed_initial_data()


if __name__ == "__main__":
    init()
