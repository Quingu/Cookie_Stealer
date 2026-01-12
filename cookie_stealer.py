import time
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from colorama import Fore, Style, init

init(autoreset=True)

# Cookies que estamos caçando
TARGET_COOKIES = [
    "JSESSIONID", "PHPSESSID", "ASP.NET_SessionId", 
    "access_token", "Authorization", "auth", 
    "ticket", "session", "token", "uid", "admin"
]

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--ignore-certificate-errors")
    
    service = Service('/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def steal_cookies(url, output_file):
    print(f"{Fore.CYAN}[*] Acessando {url} para inspeção de Storage...")
    
    driver = setup_driver()
    try:
        driver.get(url)
        time.sleep(5) # Tempo para os cookies serem setados

        # Pega todos os cookies do domínio
        all_cookies = driver.get_cookies()
        
        found_important = []
        
        print(f"{Fore.YELLOW}[*] Total de cookies encontrados: {len(all_cookies)}")
        
        with open(output_file, "w") as f:
            f.write(f"--- COOKIES CAPTURADOS: {url} ---\n\n")
            
            for cookie in all_cookies:
                name = cookie['name']
                value = cookie['value']
                domain = cookie.get('domain', 'N/A')
                
                # Verifica se o nome do cookie contém algo da nossa lista alvo
                # Usamos lower() para garantir que "Session" pegue "session"
                is_target = any(target.lower() in name.lower() for target in TARGET_COOKIES)
                
                # Ignora cookies inúteis de rastreamento/idioma
                if "i18n" in name or "ga" in name or "_gid" in name:
                    continue

                if is_target:
                    print(f"{Fore.GREEN}[+] ALVO ENCONTRADO: {name}")
                    print(f"{Fore.WHITE}    Valor: {value[:50]}...") # Mostra só o começo
                    
                    full_dump = f"[ALVO] Nome: {name} | Domínio: {domain}\nValor: {value}\n"
                    f.write(full_dump + "-"*40 + "\n")
                    found_important.append(name)
                else:
                    # Loga cookies desconhecidos mas que não são lixo óbvio
                    f.write(f"[OUTRO] {name}: {value[:30]}...\n")

        if found_important:
            print(f"\n{Fore.GREEN}[!!!] SUCESSO! Encontramos {len(found_important)} cookies de sessão potenciais.")
            print(f"Confira os valores completos em '{output_file}' e tente usar no EditThisCookie.")
        else:
            print(f"\n{Fore.RED}[-] Nenhum cookie de sessão óbvio (JSESSIONID/Auth) encontrado.")
            print("O site pode estar usando LocalStorage ou HttpOnly muito restrito.")

    except Exception as e:
        print(f"{Fore.RED}[!] Erro: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", required=True)
    parser.add_argument("-o", "--output", default="cookies_encontrados.txt")
    args = parser.parse_args()
    
    steal_cookies(args.url, args.output)
