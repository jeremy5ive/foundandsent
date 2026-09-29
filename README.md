Found & Sent
A digital archive of vintage postcards, with one new card published every morning.

🌐 foundandsent.net

Found & Sent preserves old postcards (the pictures, the handwriting, and the everyday messages people sent) so they can be searched, mapped, and read by anyone. The archive has grown to 200+ cards and keeps growing.


What's on the site
Every card, front and back, with the handwritten message transcribed
Map view that pins each card to its location
Timeline view to browse the collection by year
Search and tag filters (trips, family, holidays, locations, historical)
RSS feed so followers get each new card as it's published


How it works
Once a week I scan that week's cards. After that, the pipeline does the rest and publishes one card a day with no manual steps.

flowchart LR

    A[Scan postcards<br/>front + back] --> B[Transcribe messages<br/>with Claude]

    B --> C[queue.json<br/>+ images/]

    C --> D[GitHub Actions<br/>daily at 8am]

    D --> E[publish_card.py]

    E --> F[index.html<br/>card + map pin]

    E --> G[feed.xml<br/>RSS item]

    F --> H[GitHub Pages<br/>+ Cloudflare]

    G --> H

Scan. I scan the front and back of each card and name the image files.
Transcribe. I use Claude to read the handwriting and pull out the details: location, year, sender, recipient, and the message itself. This is the step that gives each card its meaning.
Queue. Card details go into queue.json and the images go into images/.
Publish. A scheduled GitHub Actions workflow runs publish_card.py every morning. The script:
takes the next card off the queue
checks that both images exist, and stops with a clear error if either is missing
adds the card and its map pin to index.html
adds a new item to the top of feed.xml and updates the feed date
commits the changes
Serve. The site is hosted on GitHub Pages with a custom domain through Cloudflare.


Repo layout
Path
What it is
index.html
The site: card data, map, timeline, search, and filters
feed.xml
RSS feed, updated each time a card is published
publish_card.py
Daily publishing script
queue.json
Cards waiting to be published, in order
images/
Front and back scans ({year} - {Location} - front.jpeg)
.github/workflows/
Scheduled daily publish workflow
CNAME
Custom domain for GitHub Pages



Built with
Python · GitHub Actions · GitHub Pages · Cloudflare · HTML/JavaScript · RSS · Claude (AI transcription and coding partner)


About
Found & Sent started as a hobby and is growing into a public archive. It's built and maintained by Jeremy Schwenk.
