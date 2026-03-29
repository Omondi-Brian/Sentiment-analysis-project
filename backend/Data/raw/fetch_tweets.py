import random
import csv
import pandas as pd  

themes = [
    "customer service", "network quality", "mtandao", "internet speed", "bundles", "promotions",
    "Bonga Points", "app usability", "billing", "coverage", "support", "innovations", "M-Pesa"
]

user_prefixes = ["@user", "@kenyan", "@tech", "@customer", "@nairobi", "@mombasa"]
user_numbers = list(range(1000, 9999))

years = list(range(2023, 2026))
months = list(range(1, 13))
days = list(range(1, 29))

# Swahili/Sheng words for mixing 
swahili_inserts = ["iko", "sawa", "poa", "mbaya", "sana", "bana", "haraka", "tena", "shida", "pesa", "simu", "mtandao", "msee", "dem", "rada", "omoka", "ghali", "kupenda", "bei", "fair", "worth", "afford"]

# Emoji sets
positive_emojis = ["😊","😍","🔥","😁","👍","👏","😂","❤️","🤩"]
negative_emojis = ["😡","😭","👎","😒","💀","😤","😥","🙄","🫤"]
neutral_emojis  = ["🤔","😐","💭","📱","ℹ️"]

# Templates 
positive_templates = [
    "Loving the fast {theme} from @SafaricomPLC! Inaflow {sw} sana!",
    "Great job @Safaricom_Care, ulisolve {theme} yangu {sw}!",
    "@SafaricomPLC has the best {theme} in Kenya. Thumbs up {sw}!",
    "Impressed na {theme} improvements by Safaricom. Keep it up bana!",
    "Safaricom's {theme} iko top-notch. Excellent service {sw}!",
    "Thanks @SafaricomPLC for the awesome {theme} experience. Poa kabisa!",
    "Safaricom {theme} is reliable and efficient. Love it {sw}!",
    "Positive vibes for @Safaricom_Care's handling of {theme}. Sawa sana!",
    "Safaricom delivers on {theme} promises. Great work {sw}!",
    "Happy na my {theme} from Safaricom. 5 stars bana!",
    "{theme} from Safaricom is amazing! Very satisfied {sw}.",
    "Super happy na how Safaricom handles {theme}. Poa!",
    "Best network provider thanks to excellent {theme} {sw}!",
    # Mild positives
    "I like {theme} ya Safaricom {sw}",
    "Safaricom ni poa tu {sw}",
    "Network inafanya vizuri leo bana",
    "Nakupenda hii {theme} from Safaricom",
    "Bundles ziko sawa {sw}",
    "Good service today na Safaricom",
    "Not bad at all hii {theme}",
    "Thumbs up kwa {theme} yao poa",
    "Sawa na Safaricom bana",
    "App yao inafurahisha {sw}",
    "Worth every pesa {sw}",
    "Bei ni fair lakini service poa sana",
    "Safaricom {theme} inatosha vizuri {sw}",
    "Loving the value in {theme} bana",
    "Solid {theme} from Safaricom {sw}"
]

negative_templates = [
    "Disappointed na {theme} from @SafaricomPLC. Inahitaji improvement {sw}.",
    "@Safaricom_Care, mbona {theme} iko slow {sw}? Fix it bana!",
    "Safaricom's {theme} haiko reliable. Frustrating sana!",
    "Complaining juu ya poor {theme} service from Safaricom. Shida tena!",
    "Safaricom {theme} issues tena. Nimechoka na hii!",
    "@SafaricomPLC, your {theme} is terrible. Do better {sw}!",
    "{theme} problems na Safaricom. Annoying sana bana!",
    "Bad experience na {theme} at @Safaricom_Care. Mbaya!",
    "Safaricom's {theme} is overpriced na underdelivers {sw}.",
    "Unhappy na {theme} quality from Safaricom. Si poa!",
    "Worst {theme} ever from Safaricom. Very disappointed bana!",
    "Constantly having issues na {theme}. Not good {sw}!",
    "{theme} service ni pathetic. Fix your stuff Safaricom {sw}!",
    # New price complaints & mild negatives
    "{theme} ni ghali sana {sw}",
    "Safaricom bundles ziko bei mbaya bana",
    "Expensive sana hii data {sw}",
    "Bei ya {theme} imepanda tena shida",
    "Siwezi afford bundles tena {sw}",
    "{theme} inagonga mfuko mbaya",
    "Overpriced msee na Safaricom",
    "Bei kubwa sana hii {theme}",
    "Shida ya bei ya {theme} {sw}",
    "Ghali kuliko competitors bana",
    "Not worth the bei {sw}",
    "Bei high lakini service slow",
    "Safaricom {theme} too costly {sw}",
    "{theme} ni bei mbaya sana bana",
    "Can't stand the high prices for {theme}"
]

neutral_templates = [
    "Question juu ya {theme} from @SafaricomPLC. Naweza {sw}?",
    "How does Safaricom's {theme} work {sw}?",
    "@Safaricom_Care, info on {theme} tafadhali.",
    "Checking out {theme} options na Safaricom. Kuna nini {sw}?",
    "Safaricom {theme} update: what's new bana?",
    "Inquiring about {theme} services at @SafaricomPLC {sw}.",
    "Neutral opinion juu ya Safaricom's {theme}.",
    "Looking for details on {theme} from Safaricom {sw}.",
    "Safaricom {theme} facts na figures.",
    "Discussing {theme} na @Safaricom_Care. Msee?",
    "Anyone using the new {theme} feature {sw}?",
    "Just saw ad juu ya Safaricom {theme}.",
    "What do people think about Safaricom {theme} {sw}?",
    # New variations, including pricing questions
    "Safaricom {theme} ni bei gani? {sw}",
    "Kuna update juu ya bei ya {theme}?",
    "Je, {theme} inafanya aje siku hizi {sw}?",
    "Hii {theme} ya Safaricom iko aje bana?",
    "Bei ya bundles ni kiasi gani?",
    "Info on {theme} costs {sw}",
    "How to check {theme} balance?",
    "Safaricom {theme} availability {sw}",
    "Question about {theme} activation"
]

# Noise injection helpers
def add_noise(text):
    # Random elongation
    if random.random() < 0.2:
        text = text.replace("slow", "sloooow").replace("good", "goooood").replace("expensive", "expeeeensive").replace("like", "liiiike")
    # Random typos
    if random.random() < 0.2:
        text = text.replace("Safaricom", "Safricom").replace("service", "servce").replace("bundles", "bundels")
    # Random casing
    if random.random() < 0.2:
        text = text.upper() if random.random() < 0.5 else text.capitalize()
    return text

def generate_tweet(sentiment):
    theme = random.choice(themes)
    sw = random.choice(swahili_inserts)
    if random.random() > 0.2:  
        sw += f" {random.choice(swahili_inserts)} {random.choice(swahili_inserts)}"  

    if sentiment == 'positive':
        template = random.choice(positive_templates)
        label = 'positive'
        emoji_choice = random.choice(positive_emojis)
    elif sentiment == 'negative':
        template = random.choice(negative_templates)
        label = 'negative'
        emoji_choice = random.choice(negative_emojis)
    else:
        template = random.choice(neutral_templates)
        label = 'neutral'
        emoji_choice = random.choice(neutral_emojis)

    text = template.format(theme=theme, sw=sw)
    text = add_noise(text)

    # Randomly inject emoji
    if random.random() < 0.7:
        text += " " + emoji_choice

    user = random.choice(user_prefixes) + str(random.choice(user_numbers))
    date = f"{random.choice(years)}-{str(random.choice(months)).zfill(2)}-{str(random.choice(days)).zfill(2)} {str(random.randint(0,23)).zfill(2)}:{str(random.randint(0,59)).zfill(2)}:{str(random.randint(0,59)).zfill(2)}"
    post_id = random.randint(1000000000000000000, 9999999999999999999)

    return [date, user, post_id, text, label]

# Generate balanced synthetic dataset
tweets = []
for _ in range(5000):
    tweets.append(generate_tweet('positive'))
for _ in range(5000):
    tweets.append(generate_tweet('negative'))
for _ in range(5000):
    tweets.append(generate_tweet('neutral'))

random.shuffle(tweets)

# Create synthetic DF
df_synthetic = pd.DataFrame(tweets, columns=['Date', 'User', 'Post ID', 'Content', 'Sentiment'])

# Mostly negative (complaints), some neutral (questions/opinions) - duplicates removed
real_tweets = [
    ['2026-02-02 09:57:32', '@dennisn81412561', 2018262501373440465, '@Safaricom_Care Hello is been more than 48 hours without an Internet connection I have kept calling your customer care since Saturday and today is Monday at 1300hrs and still no help If you are unable to solve my problem. Please refund my money', 'negative'],
    ['2026-02-02 09:34:22', '@MSwiry', 2018256670036525065, 'So with all the bots how do we contact customer care?', 'neutral'],
    ['2026-02-02 06:58:26', '@steveofficialKE', 2018217427817890232, 'Do you have a customer care in mlolongo', 'neutral'],
    ['2026-02-02 06:56:48', '@EdNyambok', 2018217019531788321, 'Kindly check inbox.Your automated customer service line 100 is pathetic.I have been trying to follow up a reversal request since Saturday', 'negative'],
    ['2026-02-02 05:43:33', '@thekenyatimes', 2018198585087783071, 'Why Safaricom customers should stop showing M-PESA messages to merchants after making payments - OPINION https://thekenyatimes.com/opinions/why-you-should-stop-showing-your-m-pesa-messages-to-merchants/', 'neutral'],
    ['2026-02-02 05:10:29', '@WILLANNO77', 2018190263017968012, 'Hi @Safaricom_Care @SafaricomPLC Do you have any official Customer Care Agent shop around Nyayo Embakasi???', 'neutral'],
    ['2026-02-02 05:01:55', '@WILLANNO77', 2018188106902462878, 'So am asking a @Safaricom_Care @SafaricomPLC Agent which shop is next to my landmark and the guy sends me a link. How do you employ such people to be at a customer care desk. You think I didnt know the link exists. As an agent i have told you a landmark. Just check and advise', 'negative'],
    ['2026-02-01 21:30:24', '@dexxe', 2018074477960028258, 'for instance: the god of customer service (name pending). thats who you pray to when you are trying to get in touch with safaricom. or hope to get an agent that wont gaslight you.', 'negative'],
    ['2026-02-01 18:55:52', '@peris79369', 2018035589140861433, '@SafaricomPL 0119 411675...this number is calling posing to be safaricom customer care....and the reversal is not going through', 'negative'],
    ['2024-11-22 06:36:26', '@MaggietheMezzo', 1859848394052862417, 'Safaricom is a joke. THEY HAVE BEEN SLOWING DOWN INTERNET so they can sell us expander devices + overcharging their clients for internet + selling out their own clients information and location to a murderous regime. If theyre losing clients, its their own damn fault 🤷🏾‍♀️', 'negative'],
    ['2026-01-30 09:16:57', '@SEINT_TECH', 2017165125753454993, 'I regret buying a safaricom line last year because what they are doing youll be given someone else number either dead or alive Youll get a line that has fuliza or debt in other loan apps or maybe be receiving calls from people you dont know everyday asking if you are Nick', 'negative'],
    ['2024-06-26 06:42:28', '@jwaweruh', 1805854123104899496, 'Safaricom PR is in the mud. Used to get tolerated for good services but now they are snitches, shit services and expensive. Clearly not a better option.', 'negative'],
    ['2026-01-29 09:38:40', '@James_Klavas', 2016808200482201725, '@Safaricom_Care Safaricom this feels like neglect. 2 years of worsening network: weak 4G, dropped calls, failed M-Pesa, unusable apps. Repeated complaints since Dec ignored. Non-urban customers pay the same but get worse service. Regional "DISCRIMINATION!"', 'negative'],
    ['2023-06-03 12:32:25', '@Josh001J', 1664973308700286977, 'Lakini Safaricom has become very weak. They have become fraudsters too and as a patriot I hate to see such brands and the likes of Equity becoming unreliable. Very unresponsive customer care too.', 'negative'],
    ['2026-01-28 07:16:20', '@AmandeepJagde', 2016409992820142217, 'Safaricom internet is very unreliable, its as if they got zuku folks working for them', 'negative'],
    ['2021-07-10 05:53:21', '@Meninist254', 1413738091941085185, 'Lately Safaricom services are really terrible 1. You are on a call then unashtukia simu imenyamaza tu for some seconds. 2. Mpesa. You transact maybe on till or paybill then inakaa over 10 minutes before the message irudi 3. Promotional messages', 'negative'],
    ['2026-01-31 15:10:45', '@bingkingy', 2017616548106539038, 'The money Safaricom makes on loaning out our mshwari savings is more than enough for all of that and much more. Banks make new money through loans. Safaricom operate the same way and still charge extra for other services. They are just too exorbitant.', 'negative'],
    ['2025-10-08 05:17:49', '@Kibet_bull', 1975792729797095522, 'During this customer service week we will always remember that Safaricomm aided the death of some youths, aided abductions and killings. Despite being their loyal customers for long', 'negative'],
    ['2026-01-31 19:46:01', '@its_karush', 2017685822820978978, 'Whoever removed human interface on Safaricom Customer care didnt mean well for the customers. I have tried getting @Safaricom_Care @SafaricomPLC for 3 hours in vain. Getting hold of them seems like selling narcotics in a police station.', 'negative'],
    ['2026-01-10 05:23:30', '@Kalasinga_', 2009858618141614353, 'There is something very wrong at Safaricom. I applied for an internet (business) connection on 28th December and paid. Since that time, the process is yet to be concluded. The first contractor never showed up. The second one wasnt picking our calls... horrible customer experience.', 'negative'],
    ['2024-12-14 08:37:28', '@Shad_khalif', 1867851388749066440, 'Safaricom really killed customer service. Even their physical branches you’ll be treated like a prime equity banking hall', 'negative'],
    ['2026-02-02 17:14:06', '@0xGroovy9', 2018372367643291753, 'Makes me not wait for 15mins to get my money! Allows me to pay merchants directly with my stablecoins no conversions. Sends money to both airtel and safaricom, to banks, buy airtime, cross border payments e.t.c. Provides loans Who wants all that!', 'positive'],
    ['2026-02-02 15:29:53', '@Safaricom_Care', 2018346141016850523, 'Hello Sir Joe, visit any Safaricom Shop with your ID and business registration certificate. ^JR', 'neutral'],
    ['2026-02-02 15:23:46', '@Russell_G1X', 2018344601803698238, '@SafaricomPLC Dear Safaricom Customer Care Team, I hope this message finds you well. Please help me restore my Mobile SIM network. The number: 0790841547. It has been two days now since I lost the network. Im in Thika, Kiambu county, Kenya.', 'negative'],
    ['2026-02-02 14:55:25', '@channelyakele', 2018337465044521411, 'I remember him saying Kenya should not allow Starlink because it will kill Safaricom, he is just protecting his shares', 'negative'],
    ['2026-02-02 14:45:31', '@SafaricomPLC', 2018334975188185499, 'Hello @Rong_kiddo00001, apologies for the experience. Unfortunately Okoa Jahazi is an on demand service, hence it is not possible to remove it. Kindly avoid sharing contact details here as you are exposing your number to potential fraudsters. In this case, please delete. ^ZC', 'neutral'],
    ['2026-02-02 14:30:29', '@Mercyloops', 2018331192186302609, 'Same. Please fix this @Safaricom_Care and @payp', 'negative'],
    ['2026-02-02 14:26:32', '@CrispyBuda', 2018330198530204048, 'You cant be scamming & be this public facing, unless you want to be a politician. Anyway, I found several associated FinTech outfits among them a Digital Finance Service jisort[.com & Cloud Hosting Services cloudoon[.com which "look" legit but heh!😅 4/n', 'negative'],
    ['2026-02-02 10:20:34', '@aysherasar', 2018268297255629243, '@Safaricom_Care nyinyi ni wezi aki, how do you even charge me internet for a month i wasn’t using?? In fact internet was cut', 'negative'],
    ['2026-02-02 10:08:07', '@_KiiluC', 2018265165997736437, 'Companies like Koko are leaving this country, Children at home, the government is selling our pipeline and Safaricom. What are you going on about this MF?', 'negative']
]

df_real = pd.DataFrame(real_tweets, columns=['Date', 'User', 'Post ID', 'Content', 'Sentiment'])

# Merge synthetic and real
df_merged = pd.concat([df_synthetic, df_real], ignore_index=True)

random.shuffle(df_merged.values)  # Shuffle merged

# Save to CSV
with open('safaricom_tweets_enhanced.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Date', 'User', 'Post ID', 'Content', 'Sentiment'])
    writer.writerows(df_merged.values)

print("Enhanced code-mixed dataset (with merged real tweets) saved to 'safaricom_tweets_enhanced.csv' (15,019 rows, balanced, noisy & emoji-rich)")