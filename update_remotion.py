import json
import sys
from pathlib import Path
import whisper  # For transcription
import math     # For overlap checking
import itertools # For overlap checking

# --- Configuration ---
PROJECT_ROOT = Path()
PROPS_DIR = PROJECT_ROOT / "backend/storage/props"
REACT_ROOT_FILE = PROJECT_ROOT / "frontend/video/src/Root.tsx"
PUBLIC_DIR = PROJECT_ROOT / "frontend/video/public"
VIDEO_FPS = 30
MIN_CENTER_DISTANCE = 150  # Min px distance between element centers for overlap check
# ---------------------

# --- 1. Icon & Layout Validation ---

# This set is built directly from the icon list in your master prompt.
VALID_LUCIDE_ICONS = {
    "Cpu", "HardDrive", "Server", "Database", "CloudUpload", "CloudDownload", "Cloud", "CloudOff", "Wifi", "WifiOff", "WifiHigh", "WifiLow", "Globe", "Monitor", "Laptop", 
    "Smartphone", "Tablet", "Watch", "Headphones", "Mic", "Camera", "Video", "Webcam", "Terminal", "Code", "CodeSquare", "FileCode", "Binary", "Boxes", "Box", "Package", 
    "PackageOpen", "PackageCheck", "Container", "HardDriveDownload", "HardDriveUpload", "MemoryStick", "Usb", "Bluetooth", "BluetoothConnected", "BluetoothOff", "BluetoothSearching", 
    "Cast", "CastConnected", "Airplay", "Radio", "RadioReceiver", "CircuitBoard", "Chip", "Plug", "PlugZap", "Power", "PowerOff", "BatteryCharging", "BatteryFull", "BatteryLow", 
    "BatteryMedium", "BatteryWarning", "Brain", "BrainCircuit", "BrainCog", "Atom", "Microscope", "Flask", "Beaker", "TestTube", "TestTubes", "Dna", "GraduationCap", "BookOpen", 
    "Book", "Library", "BookMarked", "Bookmark", "BookCheck", "School", "University", "Presentation", "PresentationChart", "Calculator", "Ruler", "Compass", "Triangle", 
    "Circle", "Square", "Pentagon", "Hexagon", "Octagon", "Shapes", "Activity", "Pulse", "HeartPulse", "Stethoscope", "Pill", "Syringe", "Telescope", "Map", "MapPin", 
    "Waypoints", "Navigation", "Rocket", "Satellite", "SatelliteDish", "Orbit", "Lightbulb", "Lamp", "LampCeiling", "LampDesk", "LampFloor", "Flashlight", "Zap", "ZapOff", 
    "Flame", "Waves", "Wind", "CloudRain", "CloudSnow", "CloudDrizzle", "CloudFog", "CloudHail", "CloudLightning", "Tornado", "Rainbow", "Sun", "Moon", "Stars", "Sparkles", 
    "Sprout", "Leaf", "TreePine", "Trees", "Flower", "Bug", "Fish", "Bird", "Paw", "Squirrel", "TrendingUp", "TrendingDown", "BarChart", "BarChartHorizontal", "BarChart2", 
    "BarChart3", "BarChart4", "LineChart", "PieChart", "DollarSign", "Euro", "PoundSterling", "IndianRupee", "Yen", "Coins", "CreditCard", "Wallet", "Banknote", "Receipt", 
    "Scale", "Briefcase", "Building", "Building2", "Store", "ShoppingCart", "ShoppingBag", "ShoppingBasket", "Gift", "Tag", "Tags", "Ticket", "BadgeDollarSign", 
    "BadgePercent", "Percent", "Target", "Crosshair", "Medal", "Award", "Trophy", "Crown", "Gem", "Diamond", "HandCoins", "Handshake", "PiggyBank", "Landmark", "Vault", 
    "MessageCircle", "MessageSquare", "MessagesSquare", "Mail", "MailOpen", "MailCheck", "Send", "SendHorizontal", "Inbox", "Phone", "PhoneCall", "PhoneIncoming", "PhoneOutgoing", 
    "PhoneMissed", "PhoneOff", "VideoOff", "Voicemail", "AtSign", "Share", "Share2", "ThumbsUp", "ThumbsDown", "Heart", "HeartHandshake", "HeartCrack", "Smile", "Frown", 
    "Meh", "Annoyed", "Angry", "Laugh", "SmilePlus", "Users", "User", "UserPlus", "UserMinus", "UserCheck", "UserX", "UserCircle", "UserSquare", "Contact", "Contacts", 
    "Group", "Network", "Link", "Link2", "Unlink", "ExternalLink", "Rss", "Megaphone", "Podcast", "Bell", "BellOff", "BellRing", "BellDot", "Flag", "FlagTriangleRight", 
    "FileText", "File", "Files", "Folder", "FolderOpen", "FolderClosed", "FolderPlus", "FolderMinus", "FolderCheck", "FolderX", "FolderArchive", "FolderSync", "FolderClock", 
    "FolderHeart", "FolderLock", "FolderKey", "FileJson", "FileType", "FileSpreadsheet", "FileImage", "FileVideo", "FileAudio", "FilePdf", "FileArchive", "Download", "Upload", 
    "Import", "Export", "Save", "Copy", "Clipboard", "ClipboardCheck", "ClipboardCopy", "ClipboardList", "ClipboardPaste", "ClipboardType", "ClipboardX", "Paperclip", "Pin", 
    "PinOff", "Image", "ImagePlus", "ImageMinus", "Images", "Film", "Filmstrip", "Play", "Pause", "StopCircle", "SkipBack", "SkipForward", "FastForward", "Rewind", "Music", 
    "Music2", "Music3", "Music4", "Album", "Disc", "DiscAlbum", "Cassette", "Volume", "Volume1", "Volume2", "VolumeX", "MicOff", "AudioLines", "AudioWaveform", "Speaker", 
    "Menu", "X", "Plus", "Minus", "Check", "CheckCircle", "CheckSquare", "XCircle", "XSquare", "XOctagon", "AlertCircle", "AlertTriangle", "AlertOctagon", "Info", "HelpCircle", 
    "Settings", "SettingsX", "Sliders", "SlidersHorizontal", "SlidersVertical", "ToggleLeft", "ToggleRight", "Filter", "FilterX", "Search", "SearchX", "SearchCheck", "Eye", 
    "EyeOff", "MoreHorizontal", "MoreVertical", "ChevronUp", "ChevronDown", "ChevronLeft", "ChevronRight", "ChevronsUp", "ChevronsDown", "ChevronsLeft", "ChevronsRight", 
    "ChevronsUpDown", "ChevronsLeftRight", "Maximize", "Minimize", "Maximize2", "Minimize2", "ZoomIn", "ZoomOut", "Expand", "Shrink", "Move", "MoveHorizontal", "MoveVertical", 
    "MoveDiagonal", "GripHorizontal", "GripVertical", "Grid", "Grid2x2", "Grid3x3", "Layout", "LayoutDashboard", "LayoutGrid", "LayoutList", "LayoutTemplate", "Sidebar", 
    "SidebarClose", "SidebarOpen", "PanelTop", "PanelBottom", "PanelLeft", "PanelRight", "PanelTopOpen", "PanelBottomOpen", "PanelLeftOpen", "PanelRightOpen", "Edit", 
    "Edit2", "Edit3", "Pen", "PenTool", "Pencil", "PencilRuler", "Brush", "Palette", "Pipette", "Eraser", "Scissors", "Crop", "Wand", "Wand2", "Paintbrush", "PaintBucket", 
    "Type", "Bold", "Italic", "Underline", "Strikethrough", "AlignLeft", "AlignCenter", "AlignRight", "AlignJustify", "ListOrdered", "List", "Heading", "Heading1", 
    "Heading2", "Heading3", "Heading4", "Heading5", "Heading6", "Quote", "SquareCode", "Pilcrow", "RemoveFormatting", "Superscript", "Subscript", "IndentIncrease", 
    "IndentDecrease", "WrapText", "TextCursor", "TextCursorInput", "TextQuote", "TextSelect", "Baseline", "CaseSensitive", "CaseUpper", "CaseLower", "ALargeSmall", 
    "SpellCheck", "WholeWord", "Regex", "Columns", "Rows", "Navigation2", "NavigationOff", "MapPinned", "MapPinOff", "Route", "RouteOff", "Signpost", "SignpostBig", 
    "Milestone", "LocateFixed", "Locate", "LocateOff", "Radar", "Home", "Hotel", "Hospital", "Church", "Factory", "Warehouse", "Plane", "PlaneTakeoff", "PlaneLanding", "Car", 
    "Bus", "Train", "TrainFront", "Tram", "Ship", "Boat", "Bike", "Ambulance", "PoliceCar", "Truck", "Fuel", "ParkingCircle", "ParkingSquare", "TrafficCone", "Construction", 
    "Anchor", "Footprints", "Mountain", "Mountains", "Tent", "Camping", "Caravan", "RvTruck", "Ferry", "Lock", "LockOpen", "Unlock", "LockKeyhole", "LockKeyholeOpen", "Key", 
    "KeyRound", "KeySquare", "Shield", "ShieldCheck", "ShieldAlert", "ShieldX", "ShieldOff", "ShieldPlus", "ShieldMinus", "ShieldHalf", "ShieldBan", "Scan", "ScanFace", 
    "ScanEye", "Fingerprint", "Ban", "BanCircle", "TriangleAlert", "Siren", "AlarmSmoke", "BadgeCheck", "Verified", "Stamp", "Skull", "Radiation", "Biohazard", "CircleAlert", 
    "OctagonAlert", "FileWarning", "FileX", "FileCheck", "FileLock", "FileKey", "Clock", "Clock1", "Clock2", "Clock3", "Clock4", "Clock5", "Clock6", "Clock7", "Clock8", 
    "Clock9", "Clock10", "Clock11", "Clock12", "AlarmClock", "AlarmClockCheck", "AlarmClockOff", "AlarmClockPlus", "AlarmClockMinus", "Timer", "TimerOff", "TimerReset", 
    "Hourglass", "Calendar", "CalendarDays", "CalendarRange", "CalendarCheck", "CalendarX", "CalendarPlus", "CalendarMinus", "CalendarClock", "CalendarHeart", "CalendarSearch", 
    "History", "RotateCcw", "RotateCw", "RefreshCcw", "RefreshCw", "Undo", "Undo2", "Redo", "Redo2", "Repeat", "Repeat1", "Repeat2", "Shuffle", "Sunrise", "Sunset", 
    "SunMoon", "SunDim", "SunMedium", "SunSnow", "CloudSun", "CloudMoon", "CloudSunRain", "CloudMoonRain", "CloudDrizzle", "CloudRainWind", "CloudSnow", "CloudHail", 
    "CloudLightning", "CloudFog", "Cloudy", "Snowflake", "Thermometer", "ThermometerSun", "ThermometerSnowflake", "Gauge", "Droplet", "Droplets", "Umbrella", "UmbrellaOff", 
    "CircleDot", "CircleDashed", "SquareDashed", "TriangleAlert", "Pentagon", "Hexagon", "Octagon", "OctagonAlert", "Diamond", "Star", "StarHalf", "StarOff", "Clover", 
    "Club", "Spade", "Hash", "Equal", "NotEqual", "Infinity", "Divide", "Asterisk", "Ampersand", "Brackets", "Braces", "Parentheses", "Slash", "Backslash", "Pipe", "Coffee", 
    "CupSoda", "Beer", "Wine", "WineOff", "Martini", "Milk", "MilkOff", "IceCream", "IceCream2", "Candy", "CandyCane", "CandyCorn", "Lollipop", "Cookie", "Cake", "CakeSlice", 
    "Pizza", "Sandwich", "Salad", "Soup", "Utensils", "UtensilsCrossed", "ChefHat", "CookingPot", "Egg", "EggFried", "Apple", "Banana", "Cherry", "Citrus", "Grape", "Nut", 
    "Popcorn", "Croissant", "Drumstick", "Fish", "Beef", "Ham", "Carrot", "Pepper", "Dumbbell", "Goal", "Swords", "Sword", "Axe", "Hammer", "Wrench", "Drill", "Pickaxe", 
    "Shovel", "CirclePlay", "CirclePause", "CircleStop", "Gamepad", "Gamepad2", "Joystick", "Dice1", "Dice2", "Dice3", "Dice4", "Dice5", "Dice6", "CircleDot", "Heart", 
    "Bandage", "Cross", "FirstAid", "Accessibility", "Wheelchair", "HandHeart", "PawPrint", "Screwdriver", "Saw", "Magnet", "Torch", "Candle", "Storage"
}

def check_scene_visuals(scene, scene_index):
    """
    Checks for invalid icons and potential overlaps.
    Modifies the scene's elements in place.
    """
    elements = scene.get("visuals", {}).get("svg_elements", [])
    if not elements:
        return

    # 1. Icon Validation (This part is correct and working)
    for i, elem in enumerate(elements):
        if elem.get("type") == "lucide_icon":
            try:
                icon_data = elem.get("data", "Circle,80")
                if "," not in icon_data:
                    icon_data = f"{icon_data},80"
                    
                icon_name, icon_size = icon_data.split(",", 1)
                
                if icon_name not in VALID_LUCIDE_ICONS:
                    print(f"  WARNING (Scene {scene_index}): Icon '{icon_name}' not in Lucide list. Replacing with 'Circle'.")
                    elements[i]["data"] = f"Circle,{icon_size}" # This is the FIX
            except ValueError:
                print(f"  WARNING (Scene {scene_index}): Malformed lucide_icon data '{elem.get('data')}''. Replacing with 'Circle,80'.")
                elements[i]["data"] = "Circle,80" # This is the FIX
                
    # --- 2. NEW SMARTER Overlap Check ---
    
    # We only check types that have a meaningful center (x, y)
    # 'path' and 'line' are excluded because their (x,y) is not a center.
    checkable_elements = [
        e for e in elements 
        if e.get("type") in ["lucide_icon", "circle", "rect", "text", "equation"]
    ]

    for elem1, elem2 in itertools.combinations(checkable_elements, 2):
        try:
            x1, y1 = float(elem1.get("x", 0)), float(elem1.get("y", 0))
            x2, y2 = float(elem2.get("x", 0)), float(elem2.get("y", 0))
            
            # If coordinates are identical...
            if x1 == x2 and y1 == y2:
                types = {elem1.get("type"), elem2.get("type")}
                # ...check if it's an intentional text-in-box overlap
                if types == {"rect", "text"}:
                    continue  # This is allowed, skip this pair.

            # For all other pairs, check the distance
            distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
            
            if distance < MIN_CENTER_DISTANCE:
                print(f"  WARNING (Scene {scene_index}): Potential overlap detected!")
                print(f"    Elem 1 ({elem1.get('type')}, {elem1.get('data')}) at ({x1:.0f}, {y1:.0f})")
                print(f"    Elem 2 ({elem2.get('type')}, {elem2.get('data')}) at ({x2:.0f}, {y2:.0f})")
                print(f"    Center distance: {distance:.0f}px (min is {MIN_CENTER_DISTANCE}px)")
                # We still only warn, because fixing layout is destructive.
                # But now, the warnings are REAL problems.
        
        except Exception as e:
            print(f"  ERROR checking overlap: {e}")

# --- 2. Transcription ---

def transcribe_file(audio_file_path: Path, model):
    """
    Transcribes an audio file using the pre-loaded Whisper model
    and returns natural segments (a few words at a time).
    """
    if not audio_file_path.exists():
        print(f"  Warning: Audio file not found, skipping: {audio_file_path}")
        return []

    print(f"  Transcribing {audio_file_path.name}...")
    
    # We remove 'word_timestamps=True' to get natural segments
    result = model.transcribe(str(audio_file_path))
    
    # Format segments to match your Segment type (using .get() for safety)
    segments_data = []
    
    for seg in result.get("segments", []):
        segments_data.append(
            {
                "text": seg.get("text", "").strip(), # This is now a few words
                "start": seg.get("start"),
                "end": seg.get("end"),
            }
        )
            
    print(f"  Found {len(segments_data)} segments.")
    return segments_data

# --- 3. Main Root Creation Function ---

def create_react_root(script_id: str):
    """
    Reads a props JSON, validates visuals, generates transcriptions,
    and rebuilds the Remotion Root.tsx file.
    """
    
    # 1. Find and load the input JSON file
    json_input_file = PROPS_DIR / f"{script_id}.json"
    
    if not json_input_file.exists():
        print(f"Error: Input JSON file not found!")
        print(f"       Expected at: {json_input_file.absolute()}")
        sys.exit(1)

    print(f"Reading props from: {json_input_file}")
    with open(json_input_file, 'r', encoding='utf-8') as f:
        video_data = json.load(f)

    # --- 2. NEW: Validate visuals & Transcribe audio ---
    print("\nStarting visual checks and transcription...")
    # Load the model ONCE, saving time
    model = whisper.load_model("base") 

    for i, scene in enumerate(video_data.get("scenes", [])):
        print(f" Scene {i}: {scene['title']}")
        
        # --- Run Visual Checks ---
        check_scene_visuals(scene, i) # This now fixes icons and warns of REAL overlaps
        
        # --- Run Transcription ---
        audio_path_str = scene.get("audio_path")
        
        if not audio_path_str:
            print("  No audio_path, skipping transcription.")
            scene["transcription"] = [] # Add empty list for type safety
            continue
            
        # Create the full path to the audio file
        full_audio_path = PUBLIC_DIR / audio_path_str
        
        # Generate the transcription using the pre-loaded model
        segments = transcribe_file(full_audio_path, model)
        
        # Add the transcription data back to the scene object
        scene["transcription"] = segments

    print("Processing finished.\n")
    # --- End of new block ---

    # 3. Extract data and calculate video duration
    try:
        total_duration = video_data["total_duration_seconds"]
        duration_in_frames = int(total_duration * VIDEO_FPS)
        print(f"Video duration: {total_duration}s")
        print(f"Calculated frames: {duration_in_frames} (at {VIDEO_FPS}fps)")
    except KeyError:
        print("Error: 'total_duration_seconds' not found in JSON.")
        sys.exit(1)
    except TypeError:
        print(f"Error: 'total_duration_seconds' is not a number. Value: {video_data.get('total_duration_seconds')}")
        sys.exit(1)


    # 4. Convert the Python data back into a formatted JSON string
    # The 'video_data' variable now contains all the new transcription data!
    video_data_json_string = json.dumps(video_data, indent=2)

    # 5. Create the new Root.tsx file content
    react_file_content = f"""
import React from "react";
import {{ Composition }} from "remotion";
import {{ PaperVideoComposition }} from "./Composition";
import type {{ VideoScript }} from "./types";

// This file is auto-generated by the update_remotion.py script.
// Do not edit this file directly.
// Source JSON: {script_id}.json

const defaultProps: VideoScript = {video_data_json_string};

export const RemotionRoot: React.FC = () => {{
  return (
    <>
      <Composition
        id="PaperVideo"
        component={{PaperVideoComposition as any}}
        width={{1080}}
        height={{1920}}
        fps={{{VIDEO_FPS}}}
        durationInFrames={{{duration_in_frames}}} // {total_duration} seconds * {VIDEO_FPS}fps
        defaultProps={{defaultProps}}
      />
    </>
  );
}};
"""

    # 6. Write the new content to the Root.tsx file
    try:
        with open(REACT_ROOT_FILE, 'w', encoding='utf-8') as f:
            f.write(react_file_content)
        print(f"Successfully updated: {REACT_ROOT_FILE}")
    except Exception as e:
        print(f"Error writing to file: {e}")
        sys.exit(1)

# --- Main execution (unchanged) ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Please provide the script_id (the JSON filename without .json)")
        print("Usage: python update_remotion.py 2508.03680v1")
        sys.exit(1)
    
    script_id_from_args = sys.argv[1]
    create_react_root(script_id_from_args)