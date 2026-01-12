import streamlit as st
from supabase import create_client, Client

# --- KONFIGURACJA POŁĄCZENIA ---
URL = "https://owstplbxnwsisfkwprrh.supabase.co"
KEY = "sb_publishable_iWhD84gUp5h0kkdCTd1IFQ_zkYv65Ox"

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

try:
    supabase = init_connection()
except Exception as e:
    st.error(f"Błąd połączenia z Supabase: {e}")
    st.stop()

st.set_page_config(page_title="Zarządzanie Magazynem", layout="wide")
st.title("📦 System Zarządzania Produktami")

# --- ZAKŁADKI ---
tab1, tab2, tab3 = st.tabs([" Dodaj Produkt", "➕ Dodaj Kategorię", "📊 Podgląd i Zarządzanie"])

# --- DODAWANIE KATEGORII ---
with tab2:
    st.header("Nowa Kategoria")
    with st.form("category_form", clear_on_submit=True):
        kat_nazwa = st.text_input("Nazwa kategorii")
        kat_opis = st.text_area("Opis")
        submit_kat = st.form_submit_button("Zapisz kategorię")

        if submit_kat:
            if kat_nazwa:
                try:
                    data = {"nazwa": kat_nazwa, "opis": kat_opis}
                    supabase.table("Kategorie").insert(data).execute()
                    st.success(f"Dodano kategorię: {kat_nazwa}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Błąd zapisu: {e}")
            else:
                st.error("Nazwa kategorii jest wymagana!")

# --- DODAWANIE PRODUKTU ---
with tab1:
    st.header("Nowy Produkt")
    try:
        categories_res = supabase.table("Kategorie").select("id, nazwa").execute()
        categories_data = categories_res.data
    except Exception as e:
        st.error("Nie udało się pobrać kategorii.")
        categories_data = []
    
    if not categories_data:
        st.warning("Najpierw dodaj przynajmniej jedną kategorię w zakładce obok!")
    else:
        cat_options = {item['nazwa']: item['id'] for item in categories_data}
        
        with st.form("product_form", clear_on_submit=True):
            prod_nazwa = st.text_input("Nazwa produktu")
            prod_liczba = st.number_input("Liczba (sztuki)", min_value=0, step=1)
            prod_cena = st.number_input("Cena", min_value=0.0, step=0.01, format="%.2f")
            prod_kat_nazwa = st.selectbox("Kategoria", options=list(cat_options.keys()))
            
            submit_prod = st.form_submit_button("Dodaj produkt")
            
            if submit_prod:
                if prod_nazwa:
                    try:
                        product_data = {
                            "nazwa": prod_nazwa,
                            "liczba": prod_liczba,
                            "cena": prod_cena,
                            "kategorie_id": cat_options[prod_kat_nazwa]
                        }
                        supabase.table("Produkty").insert(product_data).execute()
                        st.success(f"Produkt '{prod_nazwa}' został dodany.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Błąd podczas dodawania produktu: {e}")
                else:
                    st.error("Nazwa produktu jest wymagana!")

# --- PODGLĄD I USUWANIE DANYCH ---
with tab3:
    st.header("Aktualny stan bazy")
    col1, col2 = st.columns(2)
    
    # KATEGORIE
    with col1:
        st.subheader("Kategorie")
        try:
            kat_view = supabase.table("Kategorie").select("id, nazwa, opis").execute()
            if kat_view.data:
                st.dataframe(kat_view.data, use_container_width=True)
                
                # Usuwanie kategorii (opcjonalnie)
                with st.expander("Usuń kategorię"):
                    kat_to_delete = st.selectbox("Wybierz kategorię do usunięcia", 
                                                options=kat_view.data, 
                                                format_func=lambda x: x['nazwa'],
                                                key="del_kat")
                    if st.button("Potwierdź usunięcie kategorii"):
                        try:
                            supabase.table("Kategorie").delete().eq("id", kat_to_delete['id']).execute()
                            st.success("Usunięto kategorię!")
                            st.rerun()
                        except Exception as e:
                            st.error("Nie można usunąć kategorii, która ma przypisane produkty!")
            else:
                st.info("Brak kategorii.")
        except Exception as e:
            st.error(f"Błąd ładowania: {e}")
    
    # PRODUKTY
    with col2:
        st.subheader("Produkty")
        try:
            prod_view = supabase.table("Produkty").select("id, nazwa, liczba, cena").execute()
            if prod_view.data:
                st.dataframe(prod_view.data, use_container_width=True)
                
                # --- SEKCJA USUWANIA PRODUKTÓW ---
                with st.expander("🗑️ Usuń produkt"):
                    prod_to_delete = st.selectbox("Wybierz produkt do usunięcia", 
                                                 options=prod_view.data, 
                                                 format_func=lambda x: f"{x['nazwa']} (ID: {x['id']})",
                                                 key="del_prod")
                    
                    # Przycisk usuwania z czerwonym kolorem (type="primary")
                    if st.button("Potwierdź usunięcie produktu", type="primary"):
                        try:
                            supabase.table("Produkty").delete().eq("id", prod_to_delete['id']).execute()
                            st.success(f"Usunięto produkt: {prod_to_delete['nazwa']}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Błąd podczas usuwania: {e}")
            else:
                st.info("Brak produktów.")
        except Exception as e:
            st.error(f"Błąd ładowania: {e}")
