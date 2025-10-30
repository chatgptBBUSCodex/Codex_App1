import os
from datetime import datetime

from flask import Flask, jsonify, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect, FlaskForm
from wtforms import HiddenField, StringField
from wtforms.validators import DataRequired, Email, Length, Regexp

from config import get_config


db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()


class Piano(db.Model):
    __tablename__ = "pianos"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(255), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Piano {self.slug}>"


class CustomerInquiry(db.Model):
    __tablename__ = "customer_inquiries"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(32), nullable=False)
    piano_type = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Asset(db.Model):
    __tablename__ = "assets"

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)
    mime = db.Column(db.String(120), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    size_bytes = db.Column(db.Integer, nullable=False)


class InquiryForm(FlaskForm):
    full_name = StringField(
        "Họ và Tên bạn",
        validators=[
            DataRequired(message="Vui lòng nhập họ và tên."),
            Length(min=2, max=80, message="Họ và tên phải từ 2 đến 80 ký tự."),
        ],
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Vui lòng nhập email."),
            Email(message="Email không hợp lệ."),
            Length(max=255, message="Email quá dài."),
        ],
    )
    phone = StringField(
        "Số điện thoại",
        validators=[
            DataRequired(message="Vui lòng nhập số điện thoại."),
            Regexp(r"^\d{8,15}$", message="Số điện thoại phải từ 8-15 chữ số."),
        ],
    )
    piano_type = HiddenField(
        "Loại Piano Quan Tâm",
        validators=[DataRequired(message="Vui lòng chọn loại piano."),],
    )

    def validate(self, **kwargs):  # pylint: disable=signature-differs
        if self.full_name.data:
            self.full_name.data = self.full_name.data.strip()
        if self.email.data:
            self.email.data = self.email.data.strip()
        if self.phone.data:
            self.phone.data = self.phone.data.strip()
        if self.piano_type.data:
            self.piano_type.data = self.piano_type.data.strip()
        rv = super().validate(**kwargs)
        if not rv:
            return False
        valid_slugs = {p.slug for p in Piano.query.all()}
        if self.piano_type.data not in valid_slugs:
            self.piano_type.errors.append("Vui lòng chọn một loại piano hợp lệ.")
            return False
        return True


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    register_routes(app)
    register_cli(app)

    return app


def register_routes(app: Flask) -> None:
    def base_context():
        pianos = Piano.query.order_by(Piano.name.asc()).all()
        form = InquiryForm()
        return {"form": form, "pianos": pianos}

    @app.route("/")
    def index():
        return render_template("index.html", **base_context())

    @app.route("/hanh-trinh")
    def hanh_trinh():
        return render_template("hanh_trinh.html", **base_context())

    @app.route("/piano-san-sang")
    def piano_san_sang():
        return render_template("piano_san_sang.html", **base_context())

    @app.route("/piano-theo-yeu-cau")
    def piano_theo_yeu_cau():
        return render_template("piano_theo_yeu_cau.html", **base_context())

    @app.route("/dich-vu-cao-cap")
    def dich_vu_cao_cap():
        return render_template("dich_vu_cao_cap.html", **base_context())

    @app.route("/showroom")
    def showroom():
        return render_template("showroom.html", **base_context())

    @app.post("/inquiry")
    def create_inquiry():
        form = InquiryForm()
        if form.validate_on_submit():
            inquiry = CustomerInquiry(
                full_name=form.full_name.data.strip(),
                email=form.email.data.strip(),
                phone=form.phone.data.strip(),
                piano_type=form.piano_type.data.strip(),
            )
            db.session.add(inquiry)
            db.session.commit()
            return jsonify({"ok": True}), 200

        errors = {field: messages for field, messages in form.errors.items()}
        return jsonify({"ok": False, "errors": errors}), 400

    @app.get("/healthz")
    def healthz():
        return jsonify({"status": "ok"}), 200


def register_cli(app: Flask) -> None:
    @app.cli.command("seed_pianos")
    def seed_pianos():
        """Seed default piano types."""
        default_pianos = [
            {
                "slug": "upright",
                "name": "Upright",
                "description": "Piano đứng cổ điển phù hợp mọi không gian.",
                "image_path": "/static/uploads/upright.jpg",
            },
            {
                "slug": "grand",
                "name": "Grand",
                "description": "Đỉnh cao âm thanh và thiết kế sang trọng.",
                "image_path": "/static/uploads/grand.jpg",
            },
            {
                "slug": "studio",
                "name": "Studio",
                "description": "Lựa chọn hoàn hảo cho phòng thu.",
                "image_path": "/static/uploads/studio.jpg",
            },
            {
                "slug": "console",
                "name": "Console",
                "description": "Phong cách cổ điển với âm sắc ấm áp.",
                "image_path": "/static/uploads/console.jpg",
            },
            {
                "slug": "spinet",
                "name": "Spinet",
                "description": "Nhỏ gọn, linh hoạt cho không gian gia đình.",
                "image_path": "/static/uploads/spinet.jpg",
            },
            {
                "slug": "square",
                "name": "Square",
                "description": "Piano square cổ điển đầy lịch sử.",
                "image_path": "/static/uploads/square.jpg",
            },
        ]

        created = 0
        for data in default_pianos:
            if not Piano.query.filter_by(slug=data["slug"]).first():
                piano = Piano(**data)
                db.session.add(piano)
                created += 1
        if created:
            db.session.commit()
            message = f"Seeded {created} piano types."
        else:
            message = "Piano types already exist."
        print(message)


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
