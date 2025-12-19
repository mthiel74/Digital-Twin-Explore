# Unity Beginner Walkthrough: Realistic Robot Arm Demo

**Audience**: Complete Unity beginners
**Goal**: Create a professional-looking robot arm visualization from scratch
**Time**: 1-2 hours
**Prerequisites**: Unity installed (any recent LTS version)

---

## Part 1: Create a New Unity Project (15 minutes)

### Step 1.1: Launch Unity Hub

1. Open **Unity Hub** (the launcher application)
2. If you see "No projects found", that's normal - we're creating your first one!

### Step 1.2: Create New Project

```
1. Click "New Project" (big button, top-right)
2. Choose template: "3D (URP)" or "3D Core"
   - URP = Better graphics, slightly more complex
   - 3D Core = Simpler, perfectly fine for learning

3. Project name: "DigitalTwinRobotArm"
4. Location: Choose somewhere you can find it
   - Suggestion: Documents/UnityProjects/

5. Click "Create Project"
6. Wait 2-3 minutes while Unity sets up
```

### Step 1.3: First Look at Unity

When Unity opens, you'll see these panels:

```
┌─────────────────────────────────────────────┐
│  Hierarchy  │      Scene View        │Insp. │
│  (objects)  │   (3D viewport)        │ector │
│             │                        │      │
├─────────────┴────────────────────────┴──────┤
│           Project (files)                   │
│           Console (messages)                │
└─────────────────────────────────────────────┘
```

**Don't panic!** We'll use these one at a time.

---

## Part 2: Copy Your Scripts (5 minutes)

### Step 2.1: Create Scripts Folder

```
1. In the "Project" panel (bottom), you'll see "Assets"
2. Right-click in empty space
3. Create > Folder
4. Name it: "Scripts"
5. Double-click to open it
```

### Step 2.2: Copy Your C# Scripts

From your GitHub project, copy these 3 files:

**From**: `/Users/thiel/Documents/GitHub/Digital-Twin-Explore/unity/Scripts/`

**Files to copy**:
- `RobotArmTelemetryClient.cs`
- `Telemetry.cs`
- `SceneBuilder.cs` (if it exists in Editor/ subfolder)

**To**: Your new Unity project's Assets/Scripts/ folder

**How**:
```
Option A (Drag & Drop):
1. Open Finder/File Explorer
2. Navigate to your GitHub folder
3. Drag the .cs files into Unity's Project panel > Scripts folder

Option B (Copy/Paste):
1. Copy files in Finder/File Explorer
2. In Unity Project panel, right-click Scripts folder
3. "Show in Explorer/Finder"
4. Paste files here
5. Unity will auto-detect them
```

**⚠️ IMPORTANT**: If you have a `SceneBuilder.cs`, it needs to go in `Assets/Scripts/Editor/`:
```
1. Inside Scripts folder, create "Editor" folder
2. Put SceneBuilder.cs in there
```

### Step 2.3: Verify Scripts Loaded

```
1. Look at Project > Scripts
2. You should see:
   - RobotArmTelemetryClient.cs
   - Telemetry.cs

3. Wait for Unity to compile (watch bottom-right corner)
4. If you see red errors, STOP and tell me - we'll fix them
5. If no errors, continue!
```

---

## Part 3: Find a Free Robot Arm Asset (15 minutes)

### Step 3.1: Open Unity Asset Store

```
1. In Unity: Window > Asset Store
   (or press Ctrl+9 / Cmd+9)

2. A web browser will open to: assetstore.unity.com
3. Log in with your Unity account
```

### Step 3.2: Search for Robot Arm

**Search terms to try** (in order of recommendation):

1. **"industrial robot arm"** + Filter: Free
2. **"robot arm rigged"** + Filter: Free
3. **"robotic arm"** + Filter: Free
4. **"mechanical arm"** + Filter: Free

### Step 3.3: What to Look For

**Good signs**:
- ✅ Says "Free" (not $5.99)
- ✅ Has separate parts (base, arm segments, gripper)
- ✅ Shows multiple pieces in the preview image
- ✅ Recent reviews (2020+)
- ✅ FBX or Unity package format

**Avoid**:
- ❌ Single solid mesh (can't rotate joints)
- ❌ "Animated only" (we need manual control)
- ❌ Too cartoony (unless that's your style)

### Step 3.4: Download Asset

```
1. Click on the asset you chose
2. Click "Add to My Assets" (if not already owned)
3. In Unity: Window > Package Manager
4. Change dropdown (top-left) to "My Assets"
5. Find your robot arm asset
6. Click "Download"
7. Wait for download to complete
8. Click "Import"
9. In the popup, click "Import" again (import everything)
```

**Alternative: If no good Unity Asset Store options**

Try **Sketchfab** instead:

```
1. Go to: sketchfab.com
2. Search: "robot arm"
3. Filter:
   - Downloadable ✓
   - Free (CC0 or CC-BY)
4. Find one with clear separate parts
5. Download as FBX
6. In Unity: Assets > Import New Asset
7. Select the downloaded FBX file
```

---

## Part 4: Basic Scene Setup (10 minutes)

### Step 4.1: Create Empty Scene

```
1. File > New Scene
2. Choose "Basic (Built-in)" or "Basic (URP)"
3. Save: Ctrl+S / Cmd+S
4. Name: "RobotArmDemo"
5. Save in Assets/Scenes/ (create Scenes folder if needed)
```

### Step 4.2: Clean Up Default Objects

```
1. In Hierarchy panel, you'll see:
   - Main Camera
   - Directional Light

2. Keep both - we need them
3. Select Main Camera
4. In Inspector (right panel):
   - Transform > Position: (0, 2, -5)
   - Transform > Rotation: (15, 0, 0)

This gives a good view of where our robot will be
```

### Step 4.3: Add a Floor

```
1. Right-click in Hierarchy
2. 3D Object > Plane
3. Rename it "Floor" (click name, type, Enter)
4. In Inspector:
   - Position: (0, 0, 0)
   - Scale: (2, 1, 2)  [makes floor bigger]
```

---

## Part 5: Build Your Robot Arm (30 minutes)

Now we'll create the robot structure that your Python script can control.

### Step 5.1: Create Root Structure

```
1. In Hierarchy, right-click > Create Empty
2. Rename to "RobotArm"
3. Position: (0, 0, 0)

4. Right-click RobotArm > Create Empty
5. Rename to "BaseTurret"
6. Position: (0, 0, 0)

Your hierarchy should look like:
RobotArm
  └─ BaseTurret
```

### Step 5.2: Find Your Imported Robot Parts

```
1. In Project panel, search for your asset name
2. Look for folder called "Models" or "Prefabs"
3. Expand the main model file (has ► arrow)
4. You should see mesh objects inside

Note: Every asset is different! Common names:
- "Base", "Platform", "Turret"
- "Arm", "Link1", "UpperArm"
- "Forearm", "Link2", "LowerArm"
- "Gripper", "Hand", "EndEffector"
```

### Step 5.3: Add the Base

```
1. Find the base/platform mesh in your asset
2. Drag it into Hierarchy onto "BaseTurret" (as child)
3. It will appear in the Scene view
4. Select it, set Position to (0, 0, 0)

If it's huge or tiny:
- Adjust Scale: Try (1, 1, 1) first
- Or (0.01, 0.01, 0.01) if it's giant
- Or (100, 100, 100) if it's microscopic
```

### Step 5.4: Add Shoulder Pivot

```
1. Right-click BaseTurret > Create Empty
2. Rename to "ShoulderPivot"
3. Position: (0, 0.2, 0)  [adjust height based on your base]

4. Find the "upper arm" or "link 1" mesh from your asset
5. Drag it as child of ShoulderPivot
6. Adjust its position so it connects to the base

Tip: The ShoulderPivot position should be at the rotation point
```

### Step 5.5: Add Elbow Pivot

```
1. Right-click ShoulderPivot > Create Empty
2. Rename to "ElbowPivot"
3. Position: (0, 1.5, 0)  [1.5m up = your link length]

4. Find the "forearm" or "link 2" mesh
5. Drag it as child of ElbowPivot
6. Position it to connect

Target hierarchy:
RobotArm
  └─ BaseTurret
      └─ [Base mesh]
      └─ ShoulderPivot
          └─ [UpperArm mesh]
          └─ ElbowPivot
              └─ [Forearm mesh]
```

### Step 5.6: Add Gripper

```
1. Right-click ElbowPivot > Create Empty
2. Rename to "GripperBase"
3. Position: (0, 1.5, 0)  [end of forearm]

4. Right-click GripperBase > Create Empty
5. Rename to "Finger1"
6. Position: (0.05, 0, 0)

7. Right-click GripperBase > Create Empty
8. Rename to "Finger2"
9. Position: (-0.05, 0, 0)

If your asset has gripper meshes:
- Drag them as children of Finger1 and Finger2
Otherwise:
- Use small cubes for now (Create > 3D Object > Cube)
- Scale to (0.02, 0.1, 0.02) to look like fingers
```

### Step 5.7: Add Cargo Box

```
1. Right-click in Hierarchy (not under RobotArm)
2. 3D Object > Cube
3. Rename to "CargoBox"
4. Position: (0.5, 0.5, 0)
5. Scale: (0.1, 0.1, 0.1)

Add a color:
1. Select CargoBox
2. Inspector > Add Component
3. Search "material"
4. Or: In Project panel, create new Material
   - Right-click > Create > Material
   - Name it "BoxMaterial"
   - Set Albedo color to orange
   - Drag onto CargoBox
```

---

## Part 6: Attach the Control Script (10 minutes)

### Step 6.1: Add Script Component

```
1. In Hierarchy, select "RobotArm" (the root)
2. In Inspector panel (right), scroll to bottom
3. Click "Add Component"
4. Search: "RobotArmTelemetryClient"
5. Click it to add

You should now see the script with lots of fields!
```

### Step 6.2: Assign References

This is the most important part! We're telling the script which objects to control.

```
TCP Connection (leave default):
- Host: 127.0.0.1
- Port: 5555

Arm Joints (drag objects from Hierarchy):
1. Find "BaseTurret" in Hierarchy
2. Drag it to "Joint1" field
3. Find "ShoulderPivot"
4. Drag to "Joint2" field
5. Find "ElbowPivot"
6. Drag to "Joint3" field

Configuration (check these values):
- Axis1: (0, 1, 0)  [Y-axis for base rotation]
- Axis2: (1, 0, 0)  [X-axis for shoulder]
- Axis3: (1, 0, 0)  [X-axis for elbow]

Offsets (start with):
- Offset1 Degrees: 180
- Offset2 Degrees: -90
- Offset3 Degrees: 0

Gripper:
1. Drag Finger1 to "Finger1" field
2. Drag Finger2 to "Finger2" field
- Gripper Open Offset: 0.08
- Gripper Closed Offset: 0.02

Cargo:
1. Drag CargoBox to "Cargo" field
```

### Step 6.3: Verify Setup

```
1. Look at Inspector with RobotArm selected
2. All fields should show object names (not "None")
3. If you see "None (Transform)", drag the object in

Example of correct setup:
✅ Joint1: BaseTurret (Transform)
✅ Joint2: ShoulderPivot (Transform)
✅ Joint3: ElbowPivot (Transform)
❌ Joint1: None (Transform) ← WRONG, needs fixing
```

---

## Part 7: Test With Python Simulation (15 minutes)

### Step 7.1: Save Your Scene

```
1. File > Save (Ctrl+S / Cmd+S)
2. Make sure you saved!
```

### Step 7.2: Start Python Simulation

Open a **new terminal** (not Unity):

```bash
cd /Users/thiel/Documents/GitHub/Digital-Twin-Explore/python
python -m twin.run_twin_stream --model arm3d --port 5555 --hz 50
```

You should see:
```
Streaming on 127.0.0.1:5555
Waiting for connection...
```

### Step 7.3: Press Play in Unity

```
1. In Unity, at the top-center, find the Play button (▶)
2. Click it
3. The scene should start running
4. Watch the Console panel (bottom) for messages
```

**What should happen**:
- Console shows "Connected" or similar
- Your robot arm starts moving!
- Gripper opens and closes
- Box gets picked up and moved

**If nothing happens**:
- Check Console for error messages
- Verify Python is running
- Check port 5555 is correct in both Python and Unity

### Step 7.4: Stop and Adjust

```
1. Click Play button again to stop
2. If the arm looked wrong, adjust:
   - Axis1, Axis2, Axis3 values
   - Offset1, Offset2, Offset3 degrees
   - Scale of your meshes
3. Save and try again
```

---

## Part 8: Improve the Look (15 minutes)

### Step 8.1: Better Lighting

```
1. Select "Directional Light" in Hierarchy
2. In Inspector:
   - Rotation: (50, -30, 0)
   - Intensity: 1.2
   - Color: Slight warm white

2. Right-click Hierarchy > Light > Directional Light
3. Rename to "Fill Light"
4. Rotation: (-30, 150, 0)
5. Intensity: 0.3
6. Color: Slight blue
```

### Step 8.2: Add Materials to Robot Parts

```
For each mesh in your robot arm:

1. Select the mesh (e.g., UpperArm mesh)
2. In Inspector, find "Materials" section
3. Click the circle next to the material name
4. Choose an existing material OR create new:

Create Metal Material:
1. Project panel > Right-click > Create > Material
2. Name: "RobotMetal"
3. In Inspector:
   - Albedo: Dark gray #3A3A3A
   - Metallic: 0.8
   - Smoothness: 0.6
4. Drag this material onto your robot meshes
```

### Step 8.3: Better Floor

```
1. Select Floor in Hierarchy
2. Create material: "FloorGrid"
3. Settings:
   - Albedo: #CCCCCC (light gray)
   - Metallic: 0
   - Smoothness: 0.2

Or search Unity Asset Store for "grid texture" (free)
```

### Step 8.4: Camera Position

```
1. Select Main Camera
2. Try different positions:
   - Position: (-3, 2, -3)  [diagonal view]
   - Rotation: (15, 45, 0)

Or better: add camera movement script (for later)
```

---

## Part 9: Record Your Demo (10 minutes)

### Step 9.1: Unity Recorder (Built-in)

```
1. Window > Package Manager
2. Search: "Recorder"
3. Install "Unity Recorder"
4. Window > General > Recorder > Recorder Window
5. Add Recorder > Movie
6. Settings:
   - Output: Choose location
   - Frame Rate: 60
   - Resolution: 1920x1080
7. Click "Start Recording"
8. Press Play
9. Let robot arm run
10. Click "Stop Recording"
```

### Step 9.2: Alternative: Screen Recording

macOS:
```
1. Cmd+Shift+5
2. Choose area
3. Press Play in Unity
4. Record
```

Windows:
```
1. Windows+G (Game Bar)
2. Click record
3. Press Play in Unity
```

---

## Troubleshooting

### "Script can't be loaded"
```
Fix: Make sure RobotArmTelemetryClient.cs and Telemetry.cs
     are in Assets/Scripts/
Wait for Unity to finish compiling (bottom-right status)
```

### "Cannot connect to 127.0.0.1:5555"
```
1. Is Python script running? Check terminal
2. Is port 5555 correct in both?
3. Try restarting both Unity and Python
```

### Robot arm rotates the wrong direction
```
Fix: Change axis values in Inspector:
Try different combinations:
- Axis1: (0, 1, 0) or (0, -1, 0) or (0, 0, 1)
- Axis2: (1, 0, 0) or (-1, 0, 0) or (0, 0, 1)
- Axis3: (1, 0, 0) or (-1, 0, 0) or (0, 1, 0)
```

### Meshes are misaligned
```
Fix: Adjust positions of child meshes
The empty GameObjects (BaseTurret, ShoulderPivot, etc.)
should be at rotation points, not the meshes
```

### Gripper doesn't move
```
1. Check Finger1 and Finger2 are assigned
2. Verify they're children of GripperBase
3. Check they move on X-axis (local space)
```

---

## Next Steps

Once you have the basic setup working:

1. **Better Assets**: Try different robot arm models
2. **Environment**: Add factory background, workbench, etc.
3. **Post-Processing**: Window > Rendering > Post-processing
4. **Animation**: Add smooth camera movement
5. **UI**: Add telemetry display (text showing joint angles)

---

## Save & Backup

```
Your project is at:
~/Documents/UnityProjects/DigitalTwinRobotArm/

Important folders:
- Assets/Scripts/ (your code)
- Assets/Scenes/ (your scene)
- Assets/Materials/ (your materials)

Backup:
1. Copy entire project folder
2. Or: Assets > Export Package (smaller)
3. Or: Use Git (recommended)
```

---

## Questions?

At each step, if something doesn't match what you see on screen, STOP and ask. Unity can look different depending on:
- Version
- Layout
- What's currently selected

Don't worry - we'll figure it out together!
