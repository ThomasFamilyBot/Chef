# ChefBot: set up your own

ChefBot is a recipe box that you run by talking to Claude. You send it a recipe (a link, a photo of a cookbook page, a typed-out card from your grandmother) and it:

- rewrites the recipe into one clean, consistent format, with the ingredients grouped the way you'd lay them out on the counter;
- works out calories, protein and fat for the whole recipe;
- publishes it to **your own recipe website**, which works on any phone;
- builds **shopping lists** that add up ingredients across recipes and sort them by store aisle, with one list per person in your house.

Optional extras: a printable Google Doc of every recipe, shopping lists that stay in sync between phones, and an email address your friends can send recipes to.

You can see what a brand-new one looks like here: [thomasfamilybot.github.io/chefbot-starter](https://thomasfamilybot.github.io/chefbot-starter/)

This guide assumes you have never heard of GitHub. Nothing here needs any technical skill. It is about fifteen minutes of clicking, then a conversation with Claude.

---

## Before you start

**You need:**

- A **paid Claude plan** (Pro or Max) at claude.ai.
- A **computer with a web browser** for the setup. Once it is running, everything works from a phone.
- About **45 minutes**. The optional extras add 10 to 15 minutes each and can wait for another day.

**It costs nothing beyond Claude.** GitHub, the website and the Google pieces are all free.

**One thing to know first: your recipe site is public.** It is not advertised anywhere, and nobody will stumble on it, but anyone who has the address can open it. So throughout this setup, use first names or nicknames only. No surnames, no home address, nothing you wouldn't put on a postcard.

### Let Claude walk you through it

You don't have to follow this guide alone. Open a new chat at claude.ai, paste in this whole guide, and add:

> I'm setting up my own ChefBot using the guide I've pasted. I have never used GitHub. Walk me through it one step at a time: give me one step, wait until I say it's done or tell you what I see, then give me the next. If my screen doesn't match the guide, help me find the right button. Never ask me for a password or a verification code. Start with "Step 1: Pick your names".

Websites move their buttons around. If something on your screen doesn't match a step below, tell Claude what you do see.

---

## Step 1: Pick your names

Decide these now and write them down. You'll be asked for each one along the way.

| What | Used for | Example | Yours |
|---|---|---|---|
| **A bot email address** (recommended) | Signing up for GitHub, and later as the address friends send recipes to | `maplestreetkitchen@gmail.com` | |
| **A GitHub username** | Becomes part of your site's address. Letters, numbers and hyphens only | `maplestreetkitchen` | |
| **A site name** | Shown at the top of your recipe site. Short is best | `Chef` or `Maple Street Kitchen` | |
| **A name for your bot** | What you'll call Claude when it's doing recipe work | `ChefBot` | |
| **Your household name** | How the bot refers to you in its notes | `the Maple Street household` | |
| **Shopping list names** | One shopping list per adult. First names or nicknames | `Sam`, `Alex` | |

Your site's address will be `https://YOUR-USERNAME.github.io/chef/`, so pick a username you're happy to text to a friend.

**About the bot email address.** We suggest making a new, free Gmail account just for this (at gmail.com, choose "Create account"). It keeps the recipe project separate from your personal email, and it means the address printed on your public site is not your real one. If you'd rather not, you can use your own email for everything; the steps are the same.

---

## Step 2: Create a GitHub account

GitHub is a free service that stores files and can turn them into a website. It is where your recipes will live. Claude does all the work there; you only need an account.

1. Go to **github.com** and click **Sign up**.
2. Enter the **email address** from Step 1, create a **password** (let your browser or password manager save it), and enter the **username** you picked.
3. Finish the "are you human" puzzle if it shows one, and click **Create account**.
4. GitHub emails you a **code**. Open that email, type the code into the GitHub page.
5. If GitHub asks questions about you or your team, look for **Skip** at the bottom. If it offers plans, choose **Free**.

You're done when you see a GitHub page with your username in the top right corner.

*Good habit:* GitHub will eventually ask you to turn on two-step sign-in. When it does, say yes and follow its prompts; it takes two minutes.

---

## Step 3: Make your own copy of ChefBot

1. Still signed in to GitHub, open [github.com/ThomasFamilyBot/chefbot-starter](https://github.com/ThomasFamilyBot/chefbot-starter)
2. Click the green **Use this template** button near the top right, then **Create a new repository**. ("Repository" is GitHub's word for a project folder.)
3. Fill in the form. **Owner** is your username (already selected). For **Repository name** type `chef`. Choose **Public** (the free website only works with Public). Leave everything else alone.
4. Click **Create repository** and wait a few seconds.

You now have your own copy at `github.com/YOUR-USERNAME/chef`. It is completely separate from ours; nothing you do affects anyone else.

---

## Step 4: Switch on your website

1. On your new repository's page, click **Settings** in the row of tabs along the top. (If the window is narrow, it's under the **…** at the end of the row.)
2. In the left-hand column, click **Pages**.
3. Under "Build and deployment", open the **Source** menu and choose **GitHub Actions**.

That's the whole step. There is no Save button; it's saved as soon as you choose it. The site appears after Claude finishes setup in Step 6.

---

## Step 5: Connect Claude to your copy

1. Open a new browser tab and go to **claude.ai/code**. Sign in to Claude if it asks.
2. Claude will ask to **connect to GitHub**. Click it. A GitHub window opens; approve it with the GitHub account you just made.
3. GitHub asks where to install the Claude app. Choose your username, pick **Only select repositories**, choose **chef** from the list, and click **Install**.
4. Back in Claude, start a **new session** and choose your repository (`YOUR-USERNAME/chef`) when it asks which one to work in.

If your repository isn't in the list, give it a minute and refresh the page.

---

## Step 6: Say "Set me up"

In that new session, type:

> Set me up.

Claude takes it from here. It will ask you, one question at a time, for the names you picked in Step 1, then fill everything in, publish your site and hand you the link. Expect about ten minutes. It finishes by adding your first real recipe, so have one ready: a link, a photo of a cookbook page, or the text.

Claude will ask permission before it changes things. That's normal; say yes.

When you get your site link, open it on your phone and use **Add to Home Screen** (in the Share menu on iPhone, the ⋮ menu on Android). It then opens like an app.

---

## Step 7: Optional extras

After the basics, Claude offers these. Take any of them now or come back later and say "set up the shared shopping lists" (or whichever one you want). Each needs a Google account, and each asks you to connect Claude to Google once (claude.ai → Settings → Connectors).

| Extra | What you get | Time |
|---|---|---|
| **Google Doc copies** | Every recipe also becomes a clean, printable Google Doc in your Drive. Edit the Doc, tell Claude "doc updated", and the site follows | 5 min |
| **Shared shopping lists** | Everyone's phone shows the same lists, live. One person plans while another shops. Stored in a Google Sheet you own | 10 min |
| **Recipe inbox** | Friends email a recipe link (or drop a photo in a shared folder); the bot adds it and emails them back the page. Can run by itself once a day | 15 min |
| **Item photos** | Send a photo of the exact yogurt you buy; it shows up when anyone taps that item on the list | none |

---

## Using it day to day

Open Claude (claude.ai/code on a computer, or the Claude app on your phone), start a session on your `chef` repository, and say what you want:

- "Add this recipe: (paste a link)"
- "Add this one" with a photo of a cookbook page. "It's from Six Seasons, page 212."
- "What goes with the lasagna?"
- "Plan dinner for eight on Saturday. Grill, not too much work."
- "Add paper towels to our House Staples list."
- "Change the shopping list names to Sam and Alex."
- "What should we add to the library next?"
- "Recalculate the nutrition for the chili."

Changes show up on your site a minute or two later. Everything is saved with full history, so nothing can be lost by accident: if a change goes wrong, say "undo that".

Other adults in the house can use the same Claude account, or their own. For their own, they repeat Step 2 (their own GitHub account), you invite them (your repository → Settings → Collaborators → Add people), and they do Step 5.

---

## If something goes wrong

- **Claude can't see my repository (Step 5).** In GitHub, click your picture (top right) → Settings → Applications → Claude → Configure, and make sure `chef` is ticked.
- **My site says "404" or "not found".** Step 4 was probably missed. Do it now, then tell Claude "the site isn't showing up" and it will publish again.
- **GitHub emailed me that something failed.** Tell Claude "GitHub says the build failed." It reads the error and fixes it.
- **A recipe site won't let Claude read the page.** Some sites block robots. Print the page to PDF (or take screenshots) and give Claude that instead.
- **I want to start over.** In GitHub: your repository → Settings → scroll to the bottom → Delete this repository. Then begin again at Step 3. Your GitHub account can stay.
- **Anything else.** Tell Claude what you were doing and what you see. It can read every file in your project and usually finds the problem quickly.

---

## Staying safe

- **Never give Claude a password or a verification code**, and it should never ask. You type those into GitHub and Google yourself.
- **Assume everything on the site is public**: recipes, notes inside them, list names, item photos. Check photos for faces, addresses and receipts before sending them.
- **Shopping lists are low-stakes by design.** If you turn on shared lists, they live in a Google Sheet behind a long unguessable web address. Fine for groceries; don't put anything private on a list.
- **Your copy is yours.** We can't see into your GitHub or Google accounts, and nothing reports back to us.
