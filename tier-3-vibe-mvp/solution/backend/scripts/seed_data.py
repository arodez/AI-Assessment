"""Pure fixture data for the initial seed — no DB session/ORM here on
purpose. The Alembic data migration (migrations/versions/0002_*) imports
this module and inserts the rows via SQLAlchemy Core, so the actual
content lives in exactly one place instead of being duplicated between a
migration and some other seed tool.

Users/Events are given explicit `id`s: this is the very first data ever
inserted into a freshly-created (empty) database, so assigning
deterministic PKs up front lets Registrations reference them directly by
number instead of needing a look-up-after-insert step inside the
migration.
"""

import shutil
from datetime import datetime

from app.config import BASE_DIR, UPLOAD_DIR

REPO_ROOT = BASE_DIR.parents[1]  # .../tier-3-vibe-mvp
PHOTO_SRC_DIR = REPO_ROOT / "mockups" / "project" / "assets" / "photos"


def copy_seed_photos() -> tuple[int, int]:
    """Copy the 7 mockup photos into uploads/events/. Idempotent: skips a
    file that's already present. Returns (copied, skipped).
    """
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    copied = skipped = 0
    for src in sorted(PHOTO_SRC_DIR.glob("*.jpg")):
        dest = UPLOAD_DIR / src.name
        if dest.exists():
            skipped += 1
            continue
        shutil.copy2(src, dest)
        copied += 1
    return copied, skipped


def _image_path(filename: str) -> str:
    # Relative to uploads/ (not an absolute filesystem path) — the future
    # API phase's static-file route resolves this against UPLOAD_DIR.parent.
    return f"events/{filename}"


USERS = [
    {
        "id": 1,
        "first_name": "Alice",
        "last_name": "Kim",
        "email": "alice.kim@company.com",
        "is_admin": True,
    },
    {
        "id": 2,
        "first_name": "Priya",
        "last_name": "Shah",
        "email": "priya.shah@company.com",
        "is_admin": True,
    },
    {
        "id": 3,
        "first_name": "Diego",
        "last_name": "Ramirez",
        "email": "diego.ramirez@company.com",
        "is_admin": False,
    },
    {
        "id": 4,
        "first_name": "Maria",
        "last_name": "Chen",
        "email": "maria.chen@company.com",
        "is_admin": False,
    },
    {
        "id": 5,
        "first_name": "Sam",
        "last_name": "O'Neil",
        "email": "sam.oneil@company.com",
        "is_admin": False,
    },
    {
        "id": 6,
        "first_name": "Jordan",
        "last_name": "Lee",
        "email": "jordan.lee@company.com",
        "is_admin": False,
    },
    {
        "id": 7,
        "first_name": "Taylor",
        "last_name": "Brooks",
        "email": "taylor.brooks@company.com",
        "is_admin": False,
    },
    {
        "id": 8,
        "first_name": "Noah",
        "last_name": "Patel",
        "email": "noah.patel@company.com",
        "is_admin": False,
    },
]

EVENTS = [
    {
        "id": 1,
        "title": "Engineering AMA: Platform Roadmap Q3",
        "start": datetime(2026, 8, 14, 12, 0),
        "end": datetime(2026, 8, 14, 13, 0),
        "spots": 40,
        "event_type": "ama",
        "location_type": "hybrid",
        "description": "Alice opens the floor to walk through what's shipping on the platform "
        "roadmap this quarter and takes live questions on priorities, timelines, "
        "and how to get involved. Attend in person or join the Zoom for remote Q&A.",
        "image": _image_path("ama-room.jpg"),
        "location": ["Auditorium A, HQ Floor 3", "https://zoom.us/j/1112223333"],
        "host_name": "Alice Kim",
        "host_team": "Platform Engineering",
    },
    {
        "id": 2,
        "title": "Ask Me Anything: New CTO Q&A",
        "start": datetime(2026, 11, 5, 16, 0),
        "end": datetime(2026, 11, 5, 17, 0),
        "spots": 100,
        "event_type": "ama",
        "location_type": "virtual",
        "description": "An unscripted conversation with our new CTO on where engineering is "
        "headed. Submit questions live or anonymously beforehand — nothing is "
        "off the table.",
        "image": _image_path("ama-room.jpg"),
        "location": ["https://meet.google.com/abc-defg-hij"],
        "host_name": "Priya Shah",
        "host_team": "Executive Office",
    },
    {
        "id": 3,
        "title": "SQL Fundamentals Study Group",
        "start": datetime(2026, 8, 20, 17, 30),
        "end": datetime(2026, 8, 20, 19, 0),
        "spots": 12,
        "event_type": "study_group",
        "location_type": "in_person",
        "description": "A hands-on session covering SELECT statements, joins, and how to write "
        "queries that don't bring the warehouse to its knees. Bring a laptop — "
        "no prior SQL experience required.",
        "image": _image_path("study-classroom.jpg"),
        "location": ["Room 4B, Learning Center"],
        "host_name": "Diego Ramirez",
        "host_team": "Data Platform",
    },
    {
        "id": 4,
        "title": "System Design Interview Prep",
        "start": datetime(2026, 9, 10, 18, 0),
        "end": datetime(2026, 9, 10, 19, 30),
        "spots": 3,
        "event_type": "study_group",
        "location_type": "hybrid",
        "description": "Small-group practice for system design interviews — whiteboarding, "
        "trade-off discussions, and peer feedback. Capped small on purpose so "
        "everyone gets time at the board.",
        "image": _image_path("study-classroom.jpg"),
        "location": ["Room 4B, Learning Center", "https://zoom.us/j/4445556666"],
        "host_name": "Maria Chen",
        "host_team": "Backend Guild",
    },
    {
        "id": 5,
        "title": "Intro to Docker Workshop",
        "start": datetime(2026, 8, 27, 10, 0),
        "end": datetime(2026, 8, 27, 12, 0),
        "spots": 20,
        "event_type": "workshop",
        "location_type": "in_person",
        "description": "From `docker run` to your first multi-stage build. Sam walks through "
        "images, volumes, and networking with live examples — come with Docker "
        "Desktop installed.",
        "image": _image_path("workshop-room.jpg"),
        "location": ["Room 12, The Studio"],
        "host_name": "Sam O'Neil",
        "host_team": "DevOps",
    },
    {
        "id": 6,
        "title": "Advanced React Patterns Workshop",
        "start": datetime(2026, 10, 2, 13, 0),
        "end": datetime(2026, 10, 2, 15, 0),
        "spots": 5,
        "event_type": "workshop",
        "location_type": "virtual",
        "description": "Deep dive into compound components, render props, and custom hooks "
        "with real examples pulled from our own codebase. Intermediate React "
        "experience assumed.",
        "image": _image_path("workshop-room.jpg"),
        "location": ["https://zoom.us/j/7778889999"],
        "host_name": "Jordan Lee",
        "host_team": "Frontend Guild",
    },
    {
        "id": 7,
        "title": "Hands-On Figma for Engineers",
        "start": datetime(2026, 9, 24, 14, 0),
        "end": datetime(2026, 9, 24, 16, 0),
        "spots": 15,
        "event_type": "workshop",
        "location_type": "in_person",
        "description": "Learn to read and lightly edit Figma files so you can self-serve small "
        "UI tweaks without pulling in a designer. Laptops with the Figma desktop "
        "app required.",
        "image": _image_path("workshop-studio.jpg"),
        "location": ["Room 12, The Studio"],
        "host_name": "Taylor Brooks",
        "host_team": "Design Systems",
    },
    {
        "id": 8,
        "title": "New Hire Meet & Greet",
        "start": datetime(2026, 12, 3, 11, 0),
        "end": datetime(2026, 12, 3, 12, 30),
        "spots": 30,
        "event_type": "other",
        "location_type": "in_person",
        "description": "A casual meet-and-greet for anyone who's joined in the last quarter — "
        "grab a coffee, meet your new teammates, and get your questions about "
        "benefits and tools answered.",
        "image": _image_path("workshop-studio.jpg"),
        "location": ["The Studio, Floor 2"],
        "host_name": "Noah Patel",
        "host_team": "People Ops",
    },
    {
        "id": 9,
        "title": "Rooftop Happy Hour",
        "start": datetime(2026, 8, 21, 17, 0),
        "end": datetime(2026, 8, 21, 19, 0),
        "spots": 50,
        "event_type": "social",
        "location_type": "in_person",
        "description": "Drinks, snacks, and no agenda. Come unwind after a long week and catch "
        "up with people outside your immediate team.",
        "image": _image_path("rooftop-lounge.jpg"),
        "location": ["Rooftop Lounge, 12th Floor"],
        "host_name": "Alice Kim",
        "host_team": "Culture & Events",
    },
    {
        "id": 10,
        "title": "Design Team Rooftop Send-Off",
        "start": datetime(2026, 11, 20, 17, 0),
        "end": datetime(2026, 11, 20, 19, 0),
        "spots": 25,
        "event_type": "social",
        "location_type": "in_person",
        "description": "Sending off two design team members moving to new roles abroad — join "
        "us for a toast and some stories from their time here.",
        "image": _image_path("rooftop-lounge.jpg"),
        "location": ["Rooftop Lounge, 12th Floor"],
        "host_name": "Jordan Lee",
        "host_team": "Culture & Events",
    },
    {
        "id": 11,
        "title": "End-of-Summer Rooftop Social",
        "start": datetime(2026, 9, 18, 17, 30),
        "end": datetime(2026, 9, 18, 20, 0),
        "spots": 6,
        "event_type": "social",
        "location_type": "in_person",
        "description": "A small, intimate send-off to summer with the rooftop crew. Limited "
        "spots — first come, first served.",
        "image": _image_path("rooftop-social.jpg"),
        "location": ["Rooftop Terrace"],
        "host_name": "Priya Shah",
        "host_team": "Culture & Events",
    },
    {
        "id": 12,
        "title": "Quarterly All-Hands Mixer",
        "start": datetime(2026, 10, 15, 17, 0),
        "end": datetime(2026, 10, 15, 19, 30),
        "spots": 80,
        "event_type": "social",
        "location_type": "in_person",
        "description": "Right after the quarterly all-hands — stick around for food, drinks, "
        "and a chance to talk to leadership informally.",
        "image": _image_path("rooftop-social.jpg"),
        "location": ["Rooftop Terrace"],
        "host_name": "Diego Ramirez",
        "host_team": "Culture & Events",
    },
    {
        "id": 13,
        "title": "Fall Rooftop Swing Party",
        "start": datetime(2026, 10, 30, 18, 0),
        "end": datetime(2026, 10, 30, 21, 0),
        "spots": 40,
        "event_type": "social",
        "location_type": "in_person",
        "description": "Live music, fall-themed cocktails, and the good swing chairs. Costumes "
        "optional but encouraged.",
        "image": _image_path("rooftop-swing.jpg"),
        "location": ["Rooftop Terrace, West Side"],
        "host_name": "Maria Chen",
        "host_team": "Culture & Events",
    },
    {
        "id": 14,
        "title": "Holiday Kickoff Rooftop Swing",
        "start": datetime(2026, 12, 11, 18, 0),
        "end": datetime(2026, 12, 11, 21, 30),
        "spots": 60,
        "event_type": "social",
        "location_type": "in_person",
        "description": "Kicking off the holiday season with the whole company invited — hot "
        "cocoa, string lights, and a playlist curated by the culture crew.",
        "image": _image_path("rooftop-swing.jpg"),
        "location": ["Rooftop Terrace, West Side"],
        "host_name": "Sam O'Neil",
        "host_team": "Culture & Events",
    },
    # --- Events 15-35: 3 more per photo (5 total each, up from 2), weighted
    # toward the near term and tapering off by year end — Aug 11, Sep 9,
    # Oct 7, Nov 5, Dec 3 events respectively, combined with events 1-14
    # above.
    {
        "id": 15,
        "title": "Engineering AMA: Infra Migration Update",
        "start": datetime(2026, 8, 12, 12, 0),
        "end": datetime(2026, 8, 12, 13, 0),
        "spots": 35,
        "event_type": "ama",
        "location_type": "hybrid",
        "description": "A status check on the datacenter-to-cloud migration — what's moved, "
        "what's next, and how it affects on-call rotations. Live Q&A either way "
        "you join.",
        "image": _image_path("ama-room.jpg"),
        "location": ["Auditorium A, HQ Floor 3", "https://zoom.us/j/2223334444"],
        "host_name": "Alice Kim",
        "host_team": "Platform Engineering",
    },
    {
        "id": 16,
        "title": "Python Fundamentals Study Group",
        "start": datetime(2026, 8, 13, 17, 30),
        "end": datetime(2026, 8, 13, 19, 0),
        "spots": 14,
        "event_type": "study_group",
        "location_type": "in_person",
        "description": "Variables, control flow, and functions for anyone new to Python or "
        "coming from another language. First of a short series — no homework "
        "required.",
        "image": _image_path("study-classroom.jpg"),
        "location": ["Room 4B, Learning Center"],
        "host_name": "Diego Ramirez",
        "host_team": "Data Platform",
    },
    {
        "id": 17,
        "title": "Git & GitHub Workflows Workshop",
        "start": datetime(2026, 8, 18, 10, 0),
        "end": datetime(2026, 8, 18, 12, 0),
        "spots": 18,
        "event_type": "workshop",
        "location_type": "in_person",
        "description": "Branching strategies, rebasing without fear, and a PR review workflow "
        "that doesn't slow anyone down. Hands-on with real repo examples.",
        "image": _image_path("workshop-room.jpg"),
        "location": ["Room 12, The Studio"],
        "host_name": "Sam O'Neil",
        "host_team": "DevOps",
    },
    {
        "id": 18,
        "title": "API Design Workshop",
        "start": datetime(2026, 8, 19, 13, 0),
        "end": datetime(2026, 8, 19, 15, 0),
        "spots": 22,
        "event_type": "workshop",
        "location_type": "virtual",
        "description": "Resource naming, versioning, and error-shape conventions — working "
        "through the tradeoffs with real examples pulled from our own services.",
        "image": _image_path("workshop-room.jpg"),
        "location": ["https://zoom.us/j/5556667777"],
        "host_name": "Jordan Lee",
        "host_team": "Frontend Guild",
    },
    {
        "id": 19,
        "title": "Accessibility in Design Workshop",
        "start": datetime(2026, 8, 25, 14, 0),
        "end": datetime(2026, 8, 25, 16, 0),
        "spots": 16,
        "event_type": "workshop",
        "location_type": "in_person",
        "description": "Color contrast, focus order, and screen-reader basics for designers "
        "and engineers alike. Bring a screen you can test on.",
        "image": _image_path("workshop-studio.jpg"),
        "location": ["Room 12, The Studio"],
        "host_name": "Taylor Brooks",
        "host_team": "Design Systems",
    },
    {
        "id": 20,
        "title": "Welcome Back Rooftop Mixer",
        "start": datetime(2026, 8, 26, 17, 0),
        "end": datetime(2026, 8, 26, 19, 0),
        "spots": 45,
        "event_type": "social",
        "location_type": "in_person",
        "description": "Kicking the fall event calendar off right — light bites, drinks, and "
        "a chance to catch up before things get busy.",
        "image": _image_path("rooftop-lounge.jpg"),
        "location": ["Rooftop Lounge, 12th Floor"],
        "host_name": "Alice Kim",
        "host_team": "Culture & Events",
    },
    {
        "id": 21,
        "title": "Summer Kickoff BBQ",
        "start": datetime(2026, 8, 28, 17, 30),
        "end": datetime(2026, 8, 28, 20, 0),
        "spots": 55,
        "event_type": "social",
        "location_type": "in_person",
        "description": "Grilling on the terrace, lawn games, and a playlist that leans more "
        "summer-road-trip than office-party. Bring an appetite.",
        "image": _image_path("rooftop-social.jpg"),
        "location": ["Rooftop Terrace"],
        "host_name": "Priya Shah",
        "host_team": "Culture & Events",
    },
    {
        "id": 22,
        "title": "AMA: Diversity & Inclusion Initiatives",
        "start": datetime(2026, 9, 2, 12, 0),
        "end": datetime(2026, 9, 2, 13, 0),
        "spots": 60,
        "event_type": "ama",
        "location_type": "virtual",
        "description": "An open conversation on this year's D&I programs, what's landed, and "
        "where we still have work to do. Anonymous question submission available.",
        "image": _image_path("ama-room.jpg"),
        "location": ["https://meet.google.com/dei-amaq3-hub"],
        "host_name": "Noah Patel",
        "host_team": "People Ops",
    },
    {
        "id": 23,
        "title": "Data Structures & Algorithms Study Group",
        "start": datetime(2026, 9, 4, 18, 0),
        "end": datetime(2026, 9, 4, 19, 30),
        "spots": 12,
        "event_type": "study_group",
        "location_type": "in_person",
        "description": "Working through common interview-style problems together — arrays, "
        "trees, and graphs this session. Bring a laptop or just pen and paper.",
        "image": _image_path("study-classroom.jpg"),
        "location": ["Room 4B, Learning Center"],
        "host_name": "Maria Chen",
        "host_team": "Backend Guild",
    },
    {
        "id": 24,
        "title": "Intro to Terraform Workshop",
        "start": datetime(2026, 9, 9, 10, 0),
        "end": datetime(2026, 9, 9, 12, 30),
        "spots": 20,
        "event_type": "workshop",
        "location_type": "hybrid",
        "description": "Writing your first modules, understanding state, and avoiding the "
        "classic footguns. Follow along locally or watch over Zoom.",
        "image": _image_path("workshop-room.jpg"),
        "location": ["Room 12, The Studio", "https://zoom.us/j/8889990000"],
        "host_name": "Sam O'Neil",
        "host_team": "DevOps",
    },
    {
        "id": 25,
        "title": "Cross-Team Trivia Night",
        "start": datetime(2026, 9, 16, 17, 30),
        "end": datetime(2026, 9, 16, 19, 30),
        "spots": 40,
        "event_type": "social",
        "location_type": "in_person",
        "description": "Mixed teams, company-history trivia, and a scoreboard that takes "
        "itself way too seriously. Prizes for the top two teams.",
        "image": _image_path("rooftop-lounge.jpg"),
        "location": ["Rooftop Lounge, 12th Floor"],
        "host_name": "Jordan Lee",
        "host_team": "Culture & Events",
    },
    {
        "id": 26,
        "title": "Product Launch Celebration",
        "start": datetime(2026, 9, 23, 17, 0),
        "end": datetime(2026, 9, 23, 19, 30),
        "spots": 70,
        "event_type": "social",
        "location_type": "in_person",
        "description": "Celebrating this quarter's launch with the whole company — a few "
        "short toasts, then the rooftop is yours for the evening.",
        "image": _image_path("rooftop-social.jpg"),
        "location": ["Rooftop Terrace"],
        "host_name": "Diego Ramirez",
        "host_team": "Culture & Events",
    },
    {
        "id": 27,
        "title": "Q3 Wrap Rooftop Social",
        "start": datetime(2026, 9, 30, 18, 0),
        "end": datetime(2026, 9, 30, 20, 30),
        "spots": 50,
        "event_type": "social",
        "location_type": "in_person",
        "description": "Closing out the quarter together before things ramp up again in Q4 — "
        "drinks, snacks, and no agenda.",
        "image": _image_path("rooftop-swing.jpg"),
        "location": ["Rooftop Terrace, West Side"],
        "host_name": "Maria Chen",
        "host_team": "Culture & Events",
    },
    {
        "id": 28,
        "title": "Product AMA: Q4 Roadmap Preview",
        "start": datetime(2026, 10, 6, 12, 0),
        "end": datetime(2026, 10, 6, 13, 0),
        "spots": 45,
        "event_type": "ama",
        "location_type": "hybrid",
        "description": "A first look at what's planned for Q4 — priorities, sequencing, and "
        "where the biggest open questions still are. Live Q&A either way you join.",
        "image": _image_path("ama-room.jpg"),
        "location": ["Auditorium A, HQ Floor 3", "https://zoom.us/j/1119998888"],
        "host_name": "Alice Kim",
        "host_team": "Platform Engineering",
    },
    {
        "id": 29,
        "title": "New Manager Onboarding",
        "start": datetime(2026, 10, 14, 11, 0),
        "end": datetime(2026, 10, 14, 13, 0),
        "spots": 20,
        "event_type": "other",
        "location_type": "in_person",
        "description": "For anyone who's stepped into a people-management role in the last "
        "quarter — expectations, resources, and an open floor for questions.",
        "image": _image_path("workshop-studio.jpg"),
        "location": ["The Studio, Floor 2"],
        "host_name": "Noah Patel",
        "host_team": "People Ops",
    },
    {
        "id": 30,
        "title": "October Sunset Social",
        "start": datetime(2026, 10, 21, 17, 30),
        "end": datetime(2026, 10, 21, 19, 30),
        "spots": 35,
        "event_type": "social",
        "location_type": "in_person",
        "description": "An easy after-work hour on the terrace as the days get shorter — "
        "drinks, a firepit, and no set agenda.",
        "image": _image_path("rooftop-swing.jpg"),
        "location": ["Rooftop Terrace, West Side"],
        "host_name": "Sam O'Neil",
        "host_team": "Culture & Events",
    },
    {
        "id": 31,
        "title": "Halloween Costume Party",
        "start": datetime(2026, 10, 29, 18, 0),
        "end": datetime(2026, 10, 29, 21, 0),
        "spots": 65,
        "event_type": "social",
        "location_type": "in_person",
        "description": "Costumes encouraged, candy guaranteed. A DJ, a costume contest, and "
        "the rooftop decked out for the occasion.",
        "image": _image_path("rooftop-social.jpg"),
        "location": ["Rooftop Terrace"],
        "host_name": "Priya Shah",
        "host_team": "Culture & Events",
    },
    {
        "id": 32,
        "title": "Kubernetes Basics Study Group",
        "start": datetime(2026, 11, 4, 17, 30),
        "end": datetime(2026, 11, 4, 19, 0),
        "spots": 15,
        "event_type": "study_group",
        "location_type": "hybrid",
        "description": "Pods, deployments, and services — enough to read a manifest and "
        "understand what's actually running. No prior k8s experience needed.",
        "image": _image_path("study-classroom.jpg"),
        "location": ["Room 4B, Learning Center", "https://zoom.us/j/3334445555"],
        "host_name": "Diego Ramirez",
        "host_team": "Data Platform",
    },
    {
        "id": 33,
        "title": "Autumn Rooftop Send-Off",
        "start": datetime(2026, 11, 11, 17, 0),
        "end": datetime(2026, 11, 11, 19, 0),
        "spots": 30,
        "event_type": "social",
        "location_type": "in_person",
        "description": "One last rooftop evening before it's too cold to enjoy it — drinks, "
        "blankets, and good company.",
        "image": _image_path("rooftop-lounge.jpg"),
        "location": ["Rooftop Lounge, 12th Floor"],
        "host_name": "Jordan Lee",
        "host_team": "Culture & Events",
    },
    {
        "id": 34,
        "title": "Friendsgiving Potluck",
        "start": datetime(2026, 11, 18, 17, 30),
        "end": datetime(2026, 11, 18, 20, 0),
        "spots": 40,
        "event_type": "social",
        "location_type": "in_person",
        "description": "Bring a dish, any dish — sign-up sheet in the invite so we don't end "
        "up with twelve pies and no mains again.",
        "image": _image_path("rooftop-swing.jpg"),
        "location": ["Rooftop Terrace, West Side"],
        "host_name": "Maria Chen",
        "host_team": "Culture & Events",
    },
    {
        "id": 35,
        "title": "Year-End Wellness Session",
        "start": datetime(2026, 12, 9, 11, 0),
        "end": datetime(2026, 12, 9, 12, 30),
        "spots": 25,
        "event_type": "other",
        "location_type": "in_person",
        "description": "A low-key session on winding down before the holidays — short "
        "guided breathing, stretching, and tips for actually disconnecting.",
        "image": _image_path("workshop-studio.jpg"),
        "location": ["The Studio, Floor 2"],
        "host_name": "Noah Patel",
        "host_team": "People Ops",
    },
]

# user_id/event_id reference the explicit ids above. Deliberately covers:
#   - event 4 (spots=3) fully booked (3 Confirmed)      -> remaining = 0
#   - event 6 (spots=5) nearly full (4 Confirmed)        -> remaining = 1
#   - event 11: 2 Confirmed + 1 Cancelled                -> proves cancel
#     is a status flip, not a row deletion
#   - events 1, 9, 13: a few Confirmed rows each, ambient realism
REGISTRATIONS = [
    # Event 1 — Engineering AMA: Platform Roadmap Q3
    {
        "id": 1,
        "user_id": 2,
        "event_id": 1,
        "status": "Confirmed",
        "sign_up_at": datetime(2026, 8, 7, 10, 0),
    },
    {
        "id": 2,
        "user_id": 4,
        "event_id": 1,
        "status": "Confirmed",
        "sign_up_at": datetime(2026, 8, 7, 12, 30),
    },
    # Event 4 — System Design Interview Prep (spots=3) -> FULL
    {
        "id": 3,
        "user_id": 3,
        "event_id": 4,
        "status": "Confirmed",
        "sign_up_at": datetime(2026, 8, 8, 9, 15),
    },
    {
        "id": 4,
        "user_id": 5,
        "event_id": 4,
        "status": "Confirmed",
        "sign_up_at": datetime(2026, 8, 8, 14, 20),
    },
    {
        "id": 5,
        "user_id": 6,
        "event_id": 4,
        "status": "Confirmed",
        "sign_up_at": datetime(2026, 8, 9, 10, 0),
    },
    # Event 6 — Advanced React Patterns Workshop (spots=5) -> nearly full
    {
        "id": 6,
        "user_id": 4,
        "event_id": 6,
        "status": "Confirmed",
        "sign_up_at": datetime(2026, 8, 9, 11, 0),
    },
    {
        "id": 7,
        "user_id": 7,
        "event_id": 6,
        "status": "Confirmed",
        "sign_up_at": datetime(2026, 8, 9, 15, 45),
    },
    {
        "id": 8,
        "user_id": 8,
        "event_id": 6,
        "status": "Confirmed",
        "sign_up_at": datetime(2026, 8, 10, 9, 30),
    },
    {
        "id": 9,
        "user_id": 3,
        "event_id": 6,
        "status": "Confirmed",
        "sign_up_at": datetime(2026, 8, 10, 13, 0),
    },
    # Event 9 — Rooftop Happy Hour
    {
        "id": 10,
        "user_id": 3,
        "event_id": 9,
        "status": "Confirmed",
        "sign_up_at": datetime(2026, 8, 8, 8, 45),
    },
    {
        "id": 11,
        "user_id": 7,
        "event_id": 9,
        "status": "Confirmed",
        "sign_up_at": datetime(2026, 8, 8, 17, 0),
    },
    {
        "id": 12,
        "user_id": 8,
        "event_id": 9,
        "status": "Confirmed",
        "sign_up_at": datetime(2026, 8, 9, 12, 15),
    },
    # Event 11 — End-of-Summer Rooftop Social (spots=6): 2 Confirmed + 1 Cancelled
    {
        "id": 13,
        "user_id": 4,
        "event_id": 11,
        "status": "Confirmed",
        "sign_up_at": datetime(2026, 8, 8, 16, 0),
    },
    {
        "id": 14,
        "user_id": 5,
        "event_id": 11,
        "status": "Confirmed",
        "sign_up_at": datetime(2026, 8, 9, 9, 0),
    },
    {
        "id": 15,
        "user_id": 6,
        "event_id": 11,
        "status": "Cancelled",
        "sign_up_at": datetime(2026, 8, 7, 18, 0),
    },
    # Event 13 — Fall Rooftop Swing Party
    {
        "id": 16,
        "user_id": 1,
        "event_id": 13,
        "status": "Confirmed",
        "sign_up_at": datetime(2026, 8, 10, 10, 0),
    },
]
