"""Generate deterministic synthetic support tickets for lecture 05.

Every authored template has a stable group id. Variants of a template are
related examples, so the lesson keeps their group together when splitting.
This dataset is a teaching fixture, not a sample of real customer language.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import string

ROOT = Path(__file__).resolve().parents[1]

# Each independently written situation yields eight varied tickets. Keeping
# variations within a group makes the group-aware split lesson meaningful.
TEMPLATES: dict[str, list[tuple[str, tuple[str, ...]]]] = {
    "billing": [
        ("My {service} statement lists {amount} for {charge}; I expected {expected}. Can you check the calculation?", ("cloud backup", "team plan", "monthly storage", "pro account", "annual renewal", "workspace")),
        ("There are two {amount} entries for {charge} in the same billing cycle. I only placed one order.", ("$18.40", "$42.00", "$7.95", "$63.20", "$12.99", "$29.00")),
        ("The invoice for {service} shows tax of {amount}, although my account is registered in {place}.", ("design suite", "analytics add-on", "email service", "hosting plan", "team workspace", "backup storage")),
        ("I changed from {old} to {new}, but this month's bill still uses the old rate.", ("monthly", "annual", "basic", "team", "starter", "standard")),
        ("Please explain the {amount} adjustment on invoice {reference}; I cannot match it to a purchase.", ("$14.25", "$31.80", "$9.60", "$55.00", "$22.10", "$6.75")),
        ("The card charge arrived on {date}, but the receipt says it covers {period}. Which date is correct?", ("April 3", "May 18", "June 2", "July 21", "August 9", "September 14")),
        ("Our finance team needs a corrected invoice with the company name {company}; the current one says {wrong}.", ("Northstar Studio", "Pine & Co", "Delta Research", "Maple Works", "Lumen Design", "Cedar Labs")),
        ("I was billed {amount} after removing {item} from the subscription before renewal.", ("the extra seat", "video storage", "the reporting add-on", "a second workspace", "the premium support option", "the archived project")),
        ("The payment page showed {quoted}, while the settled card transaction is {settled}.", ("$24.00", "$49.00", "$16.50", "$75.00", "$32.00", "$11.25")),
        ("Can you send the receipt for the {period} payment made with the card ending {digits}?", ("March", "April", "May", "June", "July", "August")),
        ("My account was charged in {currency}, though checkout displayed prices in {other_currency}.", ("euros", "pounds", "Canadian dollars", "Mexican pesos", "yen", "Australian dollars")),
        ("We cancelled {service} during the cycle. The final invoice includes a full extra month.", ("the newsletter plan", "the API package", "our team workspace", "the storage tier", "the monitoring service", "the trial upgrade")),
    ],
    "account_access": [
        ("I can no longer sign in to {service}; the page says my {credential} is not recognized.", ("the member portal", "our workspace", "the mobile account", "the billing dashboard", "the learning site", "the shared drive")),
        ("The password reset link for {service} expires as soon as I open it in {browser}.", ("the account", "my profile", "the team portal", "the customer area", "the project hub", "the reporting page")),
        ("I replaced my phone and cannot receive the login code sent to my old {channel}.", ("number", "device", "authenticator", "work phone", "SIM card", "security app")),
        ("Please update the sign-in email from {old} to {new}; I still have access to both inboxes.", ("lee@example.test", "mira@example.test", "sam@example.test", "alex@example.test", "noor@example.test", "dev@example.test")),
        ("My invitation to {workspace} says it was accepted, but I land on a page asking me to request access.", ("Orchid project", "Field team", "Q3 review", "North region", "Atlas workspace", "Studio board")),
        ("The one-time code arrives after it has already expired, usually about {delay} later.", ("three minutes", "five minutes", "ten minutes", "two minutes", "seven minutes", "four minutes")),
        ("I am locked out after several attempts and the recovery form cannot find username {name}.", ("rlopez", "mchen", "jpatel", "srivera", "akhan", "tnguyen")),
        ("The app keeps sending me back to the sign-in screen after I complete {step}.", ("two-factor verification", "the password prompt", "the email code", "the identity check", "the approval step", "the security challenge")),
        ("A former colleague still appears as the account owner; how can our administrator transfer ownership?", ("former colleague", "previous manager", "old contractor", "departed analyst", "past team lead", "retired owner")),
        ("I can open the main site, but the profile page says my session is invalid on {device}.", ("a tablet", "my laptop", "the office computer", "an Android phone", "a shared workstation", "an iPad")),
        ("The sign-up form says {address} is already registered, even though I have never used this service.", ("pat@example.test", "kim@example.test", "jo@example.test", "ren@example.test", "ari@example.test", "tay@example.test")),
        ("Could you restore access to the account I accidentally marked as closed yesterday?", ("my personal account", "our shared profile", "the workshop login", "my old workspace", "the volunteer account", "the family profile")),
    ],
    "technical_issue": [
        ("The {feature} screen freezes whenever I try to {action} in the desktop app.", ("export", "search", "calendar", "upload", "settings", "dashboard")),
        ("Since yesterday's update, {feature} returns error {code} instead of loading the results.", ("the activity feed", "the report builder", "the map view", "the editor", "the task list", "the preview")),
        ("Files larger than {size} fail at {stage}; smaller uploads finish normally.", ("20 MB", "50 MB", "100 MB", "8 MB", "75 MB", "32 MB")),
        ("The exported {format} file opens with {problem} in {program}.", ("CSV", "PDF", "XLSX", "JSON", "PNG", "DOCX")),
        ("Notifications stopped appearing on {device}, although they are enabled in settings.", ("my work phone", "the desktop app", "the tablet", "the browser", "my second laptop", "the test device")),
        ("I see {symptom} when I use {feature} on a slow connection; refreshing does not help.", ("a blank panel", "duplicate rows", "a spinning indicator", "missing labels", "an old value", "overlapping text")),
        ("The integration with {service} has not synced new records since {date}.", ("Calendar", "Drive", "Ledger", "CRM", "Forms", "Inventory")),
        ("Keyboard shortcut {shortcut} used to open {feature}, but it now inserts a character instead.", ("Ctrl+K", "Alt+Enter", "Ctrl+Shift+P", "Ctrl+J", "Alt+S", "Ctrl+E")),
        ("The mobile app closes whenever I attach a photo from {source} to a message.", ("the camera", "the gallery", "a shared album", "the clipboard", "cloud storage", "a downloaded folder")),
        ("The chart labels overlap after I set the window width to {width}; the downloaded image has the same issue.", ("640 pixels", "720 pixels", "480 pixels", "900 pixels", "560 pixels", "800 pixels")),
        ("Our webhook endpoint receives duplicate event {event} every time a record changes.", ("update", "status", "comment", "assignment", "archive", "approval")),
        ("Text pasted into {feature} loses {formatting}, while typing the same text works.", ("the rich editor", "the notes box", "the reply field", "the description area", "the form", "the announcement tool")),
    ],
    "order_status": [
        ("Could you check where order {order} is? Tracking has shown {status} since {date}.", ("48291", "73510", "19642", "84017", "35106", "62743")),
        ("The parcel for {item} was marked delivered, but nothing is at the front desk or mailbox.", ("a replacement keyboard", "two notebooks", "a cable kit", "a lamp", "a sample pack", "a monitor stand")),
        ("My order confirmation promised arrival by {date}; the tracking page still says label created.", ("Tuesday", "June 12", "the end of the week", "October 4", "Monday morning", "the 20th")),
        ("The courier's latest scan is in {place}, which is several hours from the delivery address.", ("Reno", "Austin", "Leeds", "Puebla", "Rotterdam", "Calgary")),
        ("One box from shipment {reference} arrived today. The second package has no new scan.", ("PK-1842", "PK-5310", "PK-2097", "PK-7601", "PK-3485", "PK-9123")),
        ("Please confirm whether my order is waiting for pickup or still moving through the depot.", ("the chair parts", "the lab kit", "the printed guides", "the replacement screen", "the desk organizer", "the training materials")),
        ("The delivery estimate changed from {old_date} to {new_date}; can you tell me the current arrival day?", ("Friday", "Wednesday", "August 8", "the 15th", "Monday", "September 2")),
        ("I need to change the delivery window for shipment {code}; the carrier says it is out for delivery.", ("ZX-384", "LM-205", "QR-917", "BD-461", "AT-738", "NV-526")),
        ("Tracking says the parcel was handed to a neighbor, but it does not name the building or unit.", ("my floor", "the next office", "the side entrance", "the reception desk", "the adjacent suite", "another apartment")),
        ("Has the backordered {item} shipped separately from the rest of my order?", ("blue case", "adapter", "large size", "second volume", "replacement part", "green variant")),
        ("I received a dispatch email, but the carrier website cannot find tracking number {tracking}.", ("TRK-65190", "TRK-23804", "TRK-74931", "TRK-10485", "TRK-90276", "TRK-41638")),
        ("The delivery photo shows a different doorway. My address on order {order} is correct.", ("29174", "60832", "41596", "87301", "52648", "73409")),
    ],
    "refund_return": [
        ("I would like to return {item}; it arrived {condition} and is still within the return period.", ("the desk lamp", "a headset", "the glass bottle", "a travel case", "the charger", "a notebook set")),
        ("The refund for order {order} was approved on {date}, but it has not appeared on my card.", ("39184", "72056", "14839", "60521", "83470", "26715")),
        ("Please send a prepaid label so I can send back the {item} that does not fit.", ("small jacket", "keyboard tray", "replacement strap", "left shoe", "protective cover", "mounting bracket")),
        ("I returned parcel {tracking} last week and need to know when the refund will be issued.", ("RT-19473", "RT-62051", "RT-30846", "RT-75192", "RT-48520", "RT-91367")),
        ("The item is fine, but I ordered the wrong {variant}. Can I exchange it for {replacement}?", ("color", "size", "model", "connector", "edition", "length")),
        ("I was charged a return fee of {amount}; the product page said returns were free.", ("$4.95", "$7.00", "$12.50", "$3.25", "$8.80", "$5.60")),
        ("The replacement arrived damaged too. I would prefer a refund instead of another shipment.", ("second mug", "new cable", "replacement frame", "another case", "the exchanged unit", "substitute part")),
        ("The refund confirmation lists {amount}, but I paid {paid} for the returned product.", ("$18.00", "$42.00", "$27.50", "$64.90", "$13.75", "$35.00")),
        ("I cancelled before dispatch and would like the payment returned to the original method.", ("the order", "my purchase", "the pre-order", "the duplicate item", "the accessory", "the subscription box")),
        ("The return portal rejects my receipt number {receipt}, even though the purchase was last month.", ("RC-73015", "RC-29164", "RC-64803", "RC-10597", "RC-48236", "RC-91740")),
        ("A store credit was issued, but I requested the refund to the card used at checkout.", ("the jacket", "the speaker", "the tool kit", "the backpack", "the monitor", "the storage bin")),
        ("The box included the wrong item, so I need return instructions and a refund for order {order}.", ("56390", "80417", "13752", "42968", "97531", "28604")),
    ],
}

DETAILS = ("yesterday morning", "during the usual workday", "after the latest update", "before the next scheduled delivery",
           "on the first attempt", "while checking the account", "on a second device", "after the weekend")

SLOT_VALUES = {
    "billing": {
        "service": ("cloud backup", "team plan", "monthly storage", "pro account", "annual renewal", "workspace"),
        "amount": ("$18.40", "$42.00", "$7.95", "$63.20", "$12.99", "$29.00"),
        "charge": ("seat licenses", "storage", "the renewal", "the add-on", "support", "the extra month"),
        "expected": ("$15.00", "$35.00", "$8.00", "$60.00", "$10.00", "$25.00"),
        "period": ("April", "May", "June", "July", "August", "September"),
        "old": ("monthly", "annual", "basic", "team", "starter", "standard"),
        "new": ("annual", "monthly", "team", "basic", "standard", "starter"),
        "place": ("Oaxaca", "Monterrey", "Madrid", "Dublin", "Toronto", "Lima"),
        "reference": ("INV-1842", "INV-5310", "INV-2097", "INV-7601", "INV-3485", "INV-9123"),
        "date": ("April 3", "May 18", "June 2", "July 21", "August 9", "September 14"),
        "company": ("Northstar Studio", "Pine and Co", "Delta Research", "Maple Works", "Lumen Design", "Cedar Labs"),
        "wrong": ("Northstar Ltd", "Pine Company", "Delta Labs", "Maple Studio", "Lumen Research", "Cedar Works"),
        "item": ("the extra seat", "video storage", "the reporting add-on", "a second workspace", "premium support", "the archived project"),
        "quoted": ("$24.00", "$49.00", "$16.50", "$75.00", "$32.00", "$11.25"),
        "settled": ("$26.00", "$45.00", "$18.50", "$70.00", "$30.00", "$12.25"),
        "digits": ("1042", "6621", "9384", "2057", "8146", "3709"),
        "currency": ("euros", "pounds", "Canadian dollars", "Mexican pesos", "yen", "Australian dollars"),
        "other_currency": ("US dollars", "euros", "pounds", "Canadian dollars", "Australian dollars", "yen"),
    },
    "account_access": {
        "service": ("the member portal", "our workspace", "the mobile account", "the billing dashboard", "the learning site", "the shared drive"),
        "credential": ("password", "email address", "username", "security key", "sign-in code", "account name"),
        "browser": ("Chrome", "Firefox", "Edge", "Safari", "the mobile browser", "a private window"),
        "old": ("lee@example.test", "mira@example.test", "sam@example.test", "alex@example.test", "noor@example.test", "dev@example.test"),
        "new": ("lee2@example.test", "mira2@example.test", "sam2@example.test", "alex2@example.test", "noor2@example.test", "dev2@example.test"),
        "channel": ("number", "device", "authenticator", "work phone", "SIM card", "security app"),
        "workspace": ("Orchid project", "Field team", "Q3 review", "North region", "Atlas workspace", "Studio board"),
        "delay": ("three minutes", "five minutes", "ten minutes", "two minutes", "seven minutes", "four minutes"),
        "name": ("rlopez", "mchen", "jpatel", "srivera", "akhan", "tnguyen"),
        "step": ("two-factor verification", "the password prompt", "the email code", "the identity check", "the approval step", "the security challenge"),
        "device": ("a tablet", "my laptop", "the office computer", "an Android phone", "a shared workstation", "an iPad"),
        "address": ("pat@example.test", "kim@example.test", "jo@example.test", "ren@example.test", "ari@example.test", "tay@example.test"),
    },
    "technical_issue": {
        "feature": ("export", "search", "calendar", "upload", "settings", "dashboard"),
        "action": ("open a large report", "search by date", "change a filter", "upload a document", "save preferences", "load a chart"),
        "code": ("E104", "502", "E27", "503", "E81", "504"),
        "size": ("20 MB", "50 MB", "100 MB", "8 MB", "75 MB", "32 MB"),
        "stage": ("about halfway", "the final step", "after validation", "the first minute", "the compression stage", "the last chunk"),
        "format": ("CSV", "PDF", "XLSX", "JSON", "PNG", "DOCX"),
        "problem": ("garbled characters", "missing columns", "a blank page", "incorrect line breaks", "clipped labels", "an unreadable table"),
        "program": ("Excel", "Preview", "LibreOffice", "the browser", "Numbers", "our document viewer"),
        "service": ("Calendar", "Drive", "Ledger", "CRM", "Forms", "Inventory"),
        "date": ("April 3", "May 18", "June 2", "July 21", "August 9", "September 14"),
        "device": ("my work phone", "the desktop app", "the tablet", "the browser", "my second laptop", "the test device"),
        "symptom": ("a blank panel", "duplicate rows", "a spinning indicator", "missing labels", "an old value", "overlapping text"),
        "place": ("Calendar", "Drive", "Ledger", "CRM", "Forms", "Inventory"),
        "shortcut": ("Ctrl+K", "Alt+Enter", "Ctrl+Shift+P", "Ctrl+J", "Alt+S", "Ctrl+E"),
        "source": ("the camera", "the gallery", "a shared album", "the clipboard", "cloud storage", "a downloaded folder"),
        "width": ("640 pixels", "720 pixels", "480 pixels", "900 pixels", "560 pixels", "800 pixels"),
        "event": ("update", "status", "comment", "assignment", "archive", "approval"),
        "formatting": ("bold styling", "line breaks", "numbered lists", "links", "indentation", "bullet points"),
    },
    "order_status": {
        "order": ("48291", "73510", "19642", "84017", "35106", "62743"),
        "date": ("Tuesday", "June 12", "the end of the week", "October 4", "Monday morning", "the 20th"),
        "status": ("in transit", "at the depot", "awaiting pickup", "label created", "out for delivery", "in customs"),
        "item": ("a replacement keyboard", "two notebooks", "a cable kit", "a lamp", "a sample pack", "a monitor stand"),
        "condition": ("Reno", "Austin", "Leeds", "Puebla", "Rotterdam", "Calgary"),
        "place": ("Reno", "Austin", "Leeds", "Puebla", "Rotterdam", "Calgary"),
        "reference": ("PK-1842", "PK-5310", "PK-2097", "PK-7601", "PK-3485", "PK-9123"),
        "old_date": ("Friday", "Wednesday", "August 8", "the 15th", "Monday", "September 2"),
        "new_date": ("Saturday", "Thursday", "August 10", "the 17th", "Tuesday", "September 4"),
        "code": ("ZX-384", "LM-205", "QR-917", "BD-461", "AT-738", "NV-526"),
        "tracking": ("TRK-65190", "TRK-23804", "TRK-74931", "TRK-10485", "TRK-90276", "TRK-41638"),
    },
    "refund_return": {
        "item": ("the desk lamp", "a headset", "the glass bottle", "a travel case", "the charger", "a notebook set"),
        "condition": ("scratched", "missing a part", "cracked", "the wrong color", "not powering on", "poorly packaged"),
        "order": ("39184", "72056", "14839", "60521", "83470", "26715"),
        "date": ("April 3", "May 18", "June 2", "July 21", "August 9", "September 14"),
        "tracking": ("RT-19473", "RT-62051", "RT-30846", "RT-75192", "RT-48520", "RT-91367"),
        "variant": ("color", "size", "model", "connector", "edition", "length"),
        "replacement": ("the blue one", "a medium", "model B", "USB-C", "the second edition", "a shorter cable"),
        "amount": ("$4.95", "$7.00", "$12.50", "$3.25", "$8.80", "$5.60"),
        "paid": ("$22.00", "$39.00", "$31.50", "$59.90", "$16.75", "$40.00"),
        "receipt": ("RC-73015", "RC-29164", "RC-64803", "RC-10597", "RC-48236", "RC-91740"),
    },
}


def generate(destination: Path = ROOT / "data") -> pd.DataFrame:
    """Write 480 rows: 12 independent template groups per category."""
    destination.mkdir(parents=True, exist_ok=True)
    rows = []
    for category, templates in TEMPLATES.items():
        for template_number, (template, variants) in enumerate(templates, start=1):
            group_id = f"{category}-template-{template_number:02d}"
            for variant_number in range(8):
                fields = {key: values[(variant_number + template_number - 1) % len(values)]
                          for key, values in SLOT_VALUES[category].items()}
                template_slots = [name for _, name, _, _ in string.Formatter().parse(template) if name]
                if template_slots:
                    # The per-template options are authored for its first slot.
                    # Other slots use category-wide values with a distinct meaning.
                    fields[template_slots[0]] = variants[variant_number % len(variants)]
                text = template.format_map(fields)
                if variant_number:
                    text = text.rstrip()
                    separator = " " if text.endswith((".", "?", "!")) else ". "
                    text += separator + f"For context, this came up {DETAILS[variant_number]}."
                rows.append({"ticket_id": f"T-{len(rows) + 1:04d}", "category": category,
                             "template_group": group_id, "text": text})
    frame = pd.DataFrame(rows)
    frame.to_csv(destination / "support_tickets.csv", index=False, encoding="utf-8")
    return frame


if __name__ == "__main__":
    data = generate()
    print(f"Wrote {len(data)} tickets across {data['category'].nunique()} categories and "
          f"{data['template_group'].nunique()} template groups.")
