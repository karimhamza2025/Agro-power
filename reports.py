import streamlit as st
import sqlite3
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def arabic_text(text):
    if text is None:
        return ""

    text = str(text)
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)
def get_parties():
    connection = sqlite3.connect("agro_power.db")

    data = connection.execute("""
        SELECT id, name, party_type
        FROM parties
        ORDER BY name
    """).fetchall()

    connection.close()

    return data


def get_products():
    connection = sqlite3.connect("agro_power.db")

    data = connection.execute("""
        SELECT id, name, unit
        FROM products
        ORDER BY name
    """).fetchall()

    connection.close()

    return data
def get_statement(party_id, start_date, end_date):
    connection = sqlite3.connect("agro_power.db")

    transactions = connection.execute("""
        SELECT
            t.transaction_date,
            t.permission_number,
            t.transaction_type,
            ti.value
        FROM transactions t
        JOIN transaction_items ti
            ON t.id = ti.transaction_id
        WHERE t.party_id = ?
        AND t.transaction_date BETWEEN ? AND ?
        ORDER BY t.transaction_date, t.id
    """, (
        party_id,
        start_date,
        end_date
    )).fetchall()

    payments = connection.execute("""
        SELECT
            payment_date,
            payment_type,
            amount
        FROM payments
        WHERE party_id = ?
        AND payment_date BETWEEN ? AND ?
        ORDER BY payment_date, id
    """, (
        party_id,
        start_date,
        end_date
    )).fetchall()

    connection.close()

    movements = []

    for row in transactions:
        transaction_date = row[0]
        permission_number = row[1]
        transaction_type = row[2]
        value = row[3]

        if transaction_type == "📤 الصادر":
            debit = value
            credit = 0
        else:
            debit = 0
            credit = value

        movements.append({
            "date": transaction_date,
            "description": f"إذن {permission_number} - {transaction_type}",
            "debit": debit,
            "credit": credit
        })

    for row in payments:
        payment_date = row[0]
        payment_type = row[1]
        amount = row[2]

        if payment_type == "وارد":
            debit = 0
            credit = amount
        else:
            debit = amount
            credit = 0

        movements.append({
            "date": payment_date,
            "description": f"حركة مالية - {payment_type}",
            "debit": debit,
            "credit": credit
        })

    movements.sort(key=lambda x: x["date"])

    balance = 0

    for movement in movements:
        balance += movement["debit"]
        balance -= movement["credit"]
        movement["balance"] = balance

    return movements


def get_product_movements(product_id, start_date, end_date):
    connection = sqlite3.connect("agro_power.db")

    data = connection.execute("""
        SELECT
            t.transaction_date,
            t.permission_number,
            t.transaction_type,
            p.name,
            ti.quantity,
            ti.price,
            ti.value
        FROM transactions t
        JOIN parties p
            ON t.party_id = p.id
        JOIN transaction_items ti
            ON t.id = ti.transaction_id
        WHERE ti.product_id = ?
        AND t.transaction_date BETWEEN ? AND ?
        ORDER BY t.transaction_date, t.id
    """, (
        product_id,
        start_date,
        end_date
    )).fetchall()

    connection.close()

    return data


def create_pdf(title, headers, rows, filename):
    pdfmetrics.registerFont(
        TTFont(
            "Arial",
            r"C:\Windows\Fonts\arial.ttf"
        )
    )

    pdf = canvas.Canvas(filename)

    width, height = pdf._pagesize

    y = height - 40

    pdf.setFont("Arial", 12)

    pdf.drawRightString(
        width - 40,
        y,
        arabic_text(title)
    )

    y -= 40

    column_count = len(headers)
    column_width = (width - 80) / column_count
    row_height = 25

    for row in [headers] + rows:

        x = 40

        for cell in row:

            pdf.rect(
                x,
                y - row_height,
                column_width,
                row_height
            )

            pdf.setFont("Arial", 8)

            pdf.drawCentredString(
                x + column_width / 2,
                y - 17,
                arabic_text(cell)
            )

            x += column_width

        y -= row_height

        if y < 50:
            pdf.showPage()
            pdf.setFont("Arial", 8)
            y = height - 40
    pdf.setFont("Arial", 10)
    pdf.drawRightString(
        width - 40,
        y - 20,
        arabic_text("إجمالي كشف الحساب")
    )
    pdf.save()


def account_statement_report():
    st.subheader("💰 كشف حساب")

    parties = get_parties()

    if not parties:
        st.warning("لا توجد حسابات مسجلة.")
        return

    party_names = [
        party[1]
        for party in parties
    ]

    selected_party = st.selectbox(
        "اختر العميل / المورد",
        party_names
    )

    selected_party_data = next(
        party
        for party in parties
        if party[1] == selected_party
    )

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "من تاريخ",
            key="statement_start_date"
        )

    with col2:
        end_date = st.date_input(
            "إلى تاريخ",
            key="statement_end_date"
        )

    if start_date > end_date:
        st.error(
            "تاريخ البداية يجب أن يكون قبل تاريخ النهاية."
        )
        return

    movements = get_statement(
        selected_party_data[0],
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d")
    )

    if not movements:
        st.info(
            "لا توجد حركات لهذا الحساب في الفترة المحددة."
        )
        return

    st.divider()

    st.subheader(
        f"📋 كشف حساب: {selected_party}"
    )

    total_debit = 0
    total_credit = 0

    for movement in movements:

        total_debit += movement["debit"]
        total_credit += movement["credit"]

        st.write(
            f"**{movement['date']}** | "
            f"{movement['description']} | "
            f"مدين: **{movement['debit']:,.2f}** | "
            f"دائن: **{movement['credit']:,.2f}** | "
            f"الرصيد: **{movement['balance']:,.2f}**"
        )

    final_balance = total_debit - total_credit

    st.divider()

    st.write(
        f"🔵 **إجمالي المدين:** {total_debit:,.2f}"
    )

    st.write(
        f"🟢 **إجمالي الدائن:** {total_credit:,.2f}"
    )

    st.write(
        f"💰 **الرصيد النهائي:** {final_balance:,.2f}"
    )

    pdf_rows = []

    for movement in movements:
        pdf_rows.append([
            movement["date"],
            movement["description"],
            f"{movement['debit']:,.2f}",
            f"{movement['credit']:,.2f}",
            f"{movement['balance']:,.2f}"
        ])
    pdf_rows.append([
        "",
        "الإجمالي",
        f"{total_debit:,.2f}",
        f"{total_credit:,.2f}",
        f"{final_balance:,.2f}"
    ])
    filename = "account_statement.pdf"

    create_pdf(
        f"كشف حساب - {selected_party}",
        [
            "التاريخ",
            "البيان",
            "مدين",
            "دائن",
            "الرصيد"
        ],
        pdf_rows,
        filename
    )

    with open(filename, "rb") as file:
        st.download_button(
            "📄 تحميل كشف الحساب PDF",
            data=file,
            file_name=filename,
            mime="application/pdf"
        )


def product_movement_report():
    st.subheader("📦 حركة الأصناف")

    products = get_products()

    if not products:
        st.warning("لا توجد أصناف مسجلة.")
        return

    product_names = [
        product[1]
        for product in products
    ]

    selected_product = st.selectbox(
        "اختر الصنف",
        product_names
    )

    selected_product_data = next(
        product
        for product in products
        if product[1] == selected_product
    )

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "من تاريخ",
            key="product_start_date"
        )

    with col2:
        end_date = st.date_input(
            "إلى تاريخ",
            key="product_end_date"
        )

    if start_date > end_date:
        st.error(
            "تاريخ البداية يجب أن يكون قبل تاريخ النهاية."
        )
        return

    movements = get_product_movements(
        selected_product_data[0],
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d")
    )

    if not movements:
        st.info(
            "لا توجد حركة لهذا الصنف في الفترة المحددة."
        )
        return

    st.divider()

    st.subheader(
        f"📋 حركة الصنف: {selected_product}"
    )

    total_in = 0
    total_out = 0

    pdf_rows = []

    for movement in movements:

        transaction_type = movement[2]

        if transaction_type == "📥 الوارد":
            movement_name = "وارد"
            total_in += movement[4]
        else:
            movement_name = "صادر"
            total_out += movement[4]

        st.write(
            f"**{movement[0]}** | "
            f"إذن: **{movement[1]}** | "
            f"{movement_name} | "
            f"{movement[3]} | "
            f"الكمية: **{movement[4]}** | "
            f"السعر: **{movement[5]:,.2f}** | "
            f"القيمة: **{movement[6]:,.2f}**"
        )

        pdf_rows.append([
            movement[0],
            movement[1],
            movement_name,
            movement[3],
            str(movement[4]),
            f"{movement[5]:,.2f}",
            f"{movement[6]:,.2f}"
        ])

    balance = total_in - total_out
    pdf_rows.append([
        "",
        "",
        "الإجمالي",
        "",
        f"{total_in:,.2f}",
        f"{total_out:,.2f}",
        f"{balance:,.2f}"
    ])
    st.divider()

    st.write(
        f"📥 **إجمالي الوارد:** {total_in:,.2f}"
    )

    st.write(
        f"📤 **إجمالي الصادر:** {total_out:,.2f}"
    )

    st.write(
        f"📦 **رصيد الصنف:** {balance:,.2f}"
    )

    filename = "product_movement.pdf"

    create_pdf(
        f"حركة الصنف - {selected_product}",
        [
            "التاريخ",
            "رقم الإذن",
            "الحركة",
            "العميل/المورد",
            "الكمية",
            "السعر",
            "القيمة"
        ],
        pdf_rows,
        filename
    )

    with open(filename, "rb") as file:
        st.download_button(
            "📄 تحميل حركة الصنف PDF",
            data=file,
            file_name=filename,
            mime="application/pdf"
        )


def show():

    st.header("📋 التقارير")

    report_type = st.radio(
        "نوع التقرير",
        [
            "💰 كشف حساب",
            "📦 حركة الأصناف"
        ],
        horizontal=True
    )

    st.divider()

    if report_type == "💰 كشف حساب":
        account_statement_report()

    else:
        product_movement_report()