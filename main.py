import datetime
import json
import time
from playwright.sync_api import BrowserContext, sync_playwright
from undetected_playwright import stealth_sync
from urllib.request import Request, urlopen

url = "https://mlb.tickets.com/?agency=RSXV_CONCERTS_MPV&orgid=55055&pid=9185811"
#url="https://mlb.tickets.com/?orgid=5&agency=MLB_MPV&pid=9178821&tfl=Chicago_Cubs-Tickets-Cubs_Ticket_Information-ticket_grid-x0-Desktop-Landscape&adobe_mc=MCMID=18321174151237153602684174556079492808&MCORGID=A65F776A5245B01B0A490D44%40AdobeOrg&TS=1692321695&_gl=1*t8rih2*_gcl_au*MTI0MTMxODMzNy4xNjkyMzIxNjk3&_ga=2.113070084.1012944636.1692321696-917637136.1692321696#/event/9178821/ticketlist/?view=sections&minPrice=31&maxPrice=174&quantity=1&sort=price_desc&ada=false&seatSelection=false&onlyCoupon=true&onlyVoucher=false"
#url = "https://whatsmyip.org"
def CheckAvailable(page):#Access Denied
    if page.locator(f'text="No tickets were found matching your filter criteria"').is_visible() or page.locator(f'text="Access Denied"').is_visible():
        return False
    else:
        return True

def CheckError(page):
    try:
        if page.locator(f'text="An unexpected error has occurred."').is_visible():
            return True
        else:
            return False
    except:
        return True

def SendBot(msg):
    embed = msg
    payload = json.dumps({'content': embed, 'username': 'MLB Monitor', 'avatar_url': 'https://cdn.bleacherreport.net/images/team_logos/328x328/mlb.png'})
    headers2 = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'
        }
    req = Request('https://discord.com/api/webhooks/1141893615493333133/iPYs56-1P6xmBwERAYmG4GmDfFZjOX_8SdvzVfX2VoOBad09Uv48lBw9SR4sj7_cMkej', data=payload.encode(), headers=headers2)
    urlopen(req)

with open('proxies.txt', 'r') as file:
    proxy_strings = file.readlines()

proxies = []
for proxy_str in proxy_strings:
    parts = proxy_str.split(':')
    ip_port = f"http://{parts[0]}:{parts[1]}"
    username = parts[2]
    password = parts[3]
    proxy_config = {
        "server": ip_port,
        "username": username,
        "password": password.strip("\n")
    }
    proxies.append(proxy_config)

amtfound = 0
amterror = 0

def Run(browser, proxy_config):
    global amtfound
    global amterror

    context = browser.new_context()
    stealth_sync(context)
    page = context.new_page()
    try:
        try:
            page.goto(url, timeout=30000)
        except:
            page.evaluate("window.dispatchEvent(new Event('load'));")
            #print("Loading URL is taking too long. Swapping proxies...: " + str(proxy_config))
            #return False
        while True:
            try:#Add To Cart
                if CheckError(page):
                    print("\nMost likely IP banned. Swapping proxies...: " + str(proxy_config))
                    #page.screenshot(path=str(amterror) + "IPError.png")
                    amterror +=1
                    page.context.clear_cookies()
                    context.clear_cookies()
                    browser.close()
                    break
            
                page.wait_for_selector('//*[text()="Morgan Wallen"]')
                time.sleep(2)
                
                if CheckAvailable(page) and not CheckError(page):
                    SendBot("[" + str(amtfound) + "] Found tickets! Click URL to purchase: " + url)
                    page.screenshot(path=str(amtfound) + "_Found.png")
                    print("[" + str(amtfound) + "] Found tickets!")
                    amtfound +=1

                try:
                    page.set_default_navigation_timeout(8000)
                    print(f"\rReloading page                                        ", end='', flush=True)
                    page.reload()
                except:
                    continue
                    #print("Loading is taking too long. Swapping proxies...: " + str(proxy_config))
                    #page.context.clear_cookies()
                    #context.clear_cookies()
                    #browser.close()
                    #break
                print(f"\rChecking site                                        ", end='', flush=True)
                time.sleep(5)
            except:
                page.screenshot(path=str(amterror) + "_Error.png")
                amterror +=1
                browser.close()
                break
    except:
        page.screenshot(path=str(amterror) + "_Error.png")
        amterror +=1
        page.reload()

def Main():
    with sync_playwright() as p:
        print(f"\rStarting to monitor {url}")
        while True:
            for proxy_config in proxies:
                #print(str(proxy_config))
                browser = p.chromium.launch(headless=False, proxy=proxy_config)#
                Run(browser, proxy_config)
                time.sleep(1)

Main()
