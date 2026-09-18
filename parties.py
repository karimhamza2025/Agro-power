import streamlit as st
import sqlite3


def add_party(name, party_type, phone, address, notes):
    connection = sqlite3.connect("agro_power.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO parties (name, party_type, phone, address, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (name, party_type, phone, address, notes))

    connection.commit()
    connection.close()


def get_parties():
    connection = sqlite3.connect("agro_power.db")

    data = connection.execute("""
        SELECT id, name, party_type, phone, address, notes
        FROM parties
        ORDER BY id DESC
    """).fetchall()

    connection.close()

    return data


def show():
    st.header("👥 العملاء والموردين")

    with st.form("party_form"):
        name = st.text_input("اسم العميل / المورد")

        party_type = st.selectbox(
            "نوع الحساب",
            ["عميل", "مورد", "عميل ومورد"]
        )

        phone = st.text_input("رقم الهاتف")
        address = st.text_input("العنوان")
        notes = st.text_area("ملاحظات")

        submitted = st.form_submit_button("💾 حفظ")

        if submitted:
            if name.strip() == "":
                st.error("من فضلك أدخل اسم العميل أو المورد.")
            else:
                add_party(name, party_type, phone, address, notes)
                st.success("تم حفظ البيانات بنجاح ✅")

    st.divider()

    st.subheader("📋 العملاء والموردين المسجلين")

    parties = get_parties()

    if parties:
        for party in parties:
            col1, col2 = st.columns([6, 1])

        with col1:
            st.write(
                f"**{party[1]}** | {party[2]} | "
                f"{party[3]} | {party[4]}"
            )

        with col2:
            if st.button(
                "🗑️ حذف",
                key=f"delete_party_{party[0]}"
            ):
                delete_party(party[0])
                st.success("تم حذف الحساب بنجاح ✅")
                st.rerun()