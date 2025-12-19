# Upgrading to Realistic 3D Assets

This guide shows you how to replace basic Unity primitives (cylinders, cubes) with professional-looking 3D models for your Digital Twin visualization.

## Quick Summary

**Current Setup**: Basic cylinders for robot arm links, cube for cargo
**Goal**: Realistic industrial robot arm with proper materials and lighting
**Time Needed**: 30-60 minutes
**Cost**: $0 (using free assets)

---

## Where to Find Free 3D Assets

### Recommended Sources (Quality + License)

1. **Unity Asset Store** (Best for Unity integration)
   - URL: https://assetstore.unity.com/
   - Filter: Free assets
   - Look for "robot arm", "industrial robot", "robotic arm"
   - **Recommended packages**:
     - "Industrial Robot Arm" (if available free)
     - "Simple Robots"
     - "Sci-Fi Robot Arms Pack"

2. **Sketchfab** (High quality, CC licensed)
   - URL: https://sketchfab.com/
   - Filter: Downloadable, CC Attribution or CC0
   - Search: "robot arm", "industrial arm", "robotic gripper"
   - Export format: FBX or OBJ

3. **TurboSquid** (Free section)
   - URL: https://www.turbosquid.com/Search/3D-Models/free/robot-arm
   - Filter: Free models
   - Check license for commercial use

4. **Free3D**
   - URL: https://free3d.com/
   - Search: "robot arm" or "industrial robot"
   - Multiple formats available

5. **CGTrader** (Free models section)
   - URL: https://www.cgtrader.com/free-3d-models/robot-arm
   - Good selection of industrial equipment

---

## Specific Asset Recommendations

### Option 1: Industrial Robot Arm (Most Realistic)
**What to look for**:
- 6-axis articulated arm (you'll use 3 joints)
- Separate parts for base, links, gripper
- Includes materials/textures
- FBX or Unity package format

**Example search terms**:
- "ABB robot arm"
- "KUKA arm"
- "industrial manipulator"
- "6-axis robot"

### Option 2: Sci-Fi/Clean Robot Arm (Modern Look)
**What to look for**:
- Modular design with clear joint separation
- Clean geometry (not too many polygons)
- PBR materials (Metallic/Roughness workflow)

**Example search terms**:
- "sci-fi robot arm"
- "futuristic manipulator"
- "clean industrial arm"

### Option 3: DIY with Free Parts
Combine these individual assets:
- Robot base/turret platform
- Cylindrical links (but higher quality than Unity primitives)
- Gripper mechanism
- Industrial textures/materials

---

## Step-by-Step Integration

### 1. Download and Import Asset

#### From Unity Asset Store:
```
1. Open Unity Asset Store (Window > Asset Store)
2. Search for your chosen robot arm
3. Click "Download" then "Import"
4. Import only what you need (Model, Materials, Textures)
```

#### From External Source (Sketchfab, etc.):
```
1. Download as FBX or OBJ
2. In Unity: Assets > Import New Asset
3. Drag the FBX file into your Assets/Models folder
4. Wait for Unity to process
```

### 2. Prepare the Model

#### Inspect the Hierarchy:
```
1. Drag model into scene as preview
2. Expand hierarchy to find:
   - Base/Root transform
   - Joint 1 (base rotation/turret)
   - Joint 2 (shoulder)
   - Joint 3 (elbow)
   - Gripper parts (fingers)
3. Note which objects rotate at each joint
```

#### Create Prefab Structure:
```
Your hierarchy should match:

RobotArm (Root)
  └─ BaseTurret (Joint1 - rotates on Y)
      └─ BaseModel (visual mesh)
      └─ ShoulderPivot (Joint2 - rotates on X)
          └─ UpperArmModel (visual mesh)
          └─ ElbowPivot (Joint3 - rotates on X)
              └─ ForearmModel (visual mesh)
              └─ GripperBase
                  └─ Finger1 (moves on X)
                  └─ Finger2 (moves on -X)
```

**Key Point**: The script rotates `joint1`, `joint2`, `joint3` transforms. The visual meshes should be children of these pivot points.

### 3. Replace Primitives

#### Manual Setup:
```
1. Delete your old cylinder GameObjects
2. Create empty GameObjects for each joint pivot
3. Parent the imported model pieces to these pivots
4. Ensure pivot points are at rotation centers
```

#### Example:
```csharp
// Your RobotArmTelemetryClient.cs stays the same!
// Just reassign references:

joint1 = BaseTurret    // Your new base pivot
joint2 = ShoulderPivot // Your new shoulder pivot
joint3 = ElbowPivot    // Your new elbow pivot
```

### 4. Fix Scale and Alignment

Most downloaded models won't match your 1-meter link lengths. Fix this:

```
1. Select UpperArmModel
2. In Inspector: Transform > Scale
3. Adjust Y-scale until link length ≈ 1.5m (your l1 parameter)
4. Repeat for ForearmModel
5. Adjust X/Z scale if arm is too thick/thin
```

**Tip**: Your Python simulation uses `l1=1.5, l2=1.5, l3=1.0`. Match these in Unity for accurate visualization.

### 5. Improve Materials

#### If model has basic materials:
```
1. Select each mesh
2. In Inspector: Materials
3. Click material to edit
4. Switch shader to: Standard (Unity) or URP/Lit
5. Adjust:
   - Metallic: 0.8 (for metal parts)
   - Smoothness: 0.6
   - Add normal map if included
```

#### For realistic metal:
```
1. Create new Material: Assets > Create > Material
2. Name it "IndustrialMetal"
3. Set:
   - Albedo: Dark gray (#3A3A3A)
   - Metallic: 0.9
   - Smoothness: 0.5
4. Drag onto all arm parts
```

#### For gripper fingers:
```
Different material for contrast:
- Albedo: Dark orange or yellow (#D67D00)
- Metallic: 0.7
- Smoothness: 0.4
```

### 6. Add Better Lighting

Replace default directional light:

```
Lighting Setup:
1. Main Light (Directional):
   - Intensity: 1.2
   - Color: Slight warm (#FFFAF0)
   - Angle: 45° from above

2. Fill Light (Directional):
   - Intensity: 0.3
   - Color: Cool blue (#E6F0FF)
   - Opposite side of main light

3. Environment:
   - Window > Rendering > Lighting
   - Environment > Skybox: Choose a neutral HDRI
   - Or use solid color: Light gray
```

### 7. Optional: Add Details

#### Cables/Hoses:
- Use Unity Line Renderer
- Draw from base to joints
- Material: Black rubber texture

#### Shadows:
```
For each mesh renderer:
- Cast Shadows: On
- Receive Shadows: On
```

#### Gripper Enhancements:
- Add small cylinder primitives as "bolts"
- Add a thin box as "gripper pad" texture
- Parent to finger tips

---

## Quick Asset Recommendations (Specific)

### Best Free Options (As of 2024):

1. **"Simple Industrial Robot"** (Unity Asset Store)
   - Clean, modular design
   - Easy to separate parts
   - Good materials included

2. **Sketchfab: "Industrial Robot Arm"** by various creators
   - Filter: CC-BY or CC0 license
   - Download as FBX
   - Usually well-rigged

3. **DIY with Polygon Parts**:
   - Use free "Hard Surface Kitbash" sets
   - Combine cylinders, boxes, mechanical parts
   - Still looks 10x better than Unity primitives

---

## Testing Your New Model

```bash
# Run your simulation
cd python
python -m twin.run_twin_stream --model arm3d --port 5555 --hz 50
```

In Unity:
1. Press Play
2. Watch your realistic arm move!
3. Verify all joints rotate correctly
4. Check gripper opens/closes smoothly

---

## Troubleshooting

### Model imports but looks wrong:
- **Check scale**: FBX files often import at 0.01x or 100x
- **Fix**: Select FBX in Assets, Inspector > Model > Scale Factor

### Joints rotate wrong axis:
- **Fix in RobotArmTelemetryClient**:
  ```csharp
  public Vector3 axis1 = Vector3.up;     // Try Vector3.forward
  public Vector3 axis2 = Vector3.right;  // Try Vector3.up
  ```

### Gripper doesn't open:
- **Check finger pivot points**: Must be at gripper base
- **Check local position**: Fingers should move on local X-axis

### Textures missing:
- **Extract textures**: FBX > Inspector > Materials > Extract Materials
- **Unity will create material assets**

### Model too complex (low FPS):
- **Reduce polygons**: Use Blender (free) to decimate mesh
- **Or**: Find a "low-poly" version

---

## Performance Tips

- **LOD (Level of Detail)**: Add if recording high-res videos
- **Occlusion Culling**: Enable in large scenes
- **Texture Size**: 1024x1024 is usually enough
- **Poly Count**: Aim for < 10k triangles per link

---

## Next Steps

After visual upgrade:
1. **Better floor**: Add grid texture or industrial platform
2. **Cargo box**: Replace with realistic package/crate model
3. **Environment**: Add factory background (free on Asset Store)
4. **Post-processing**: Bloom, Ambient Occlusion for polish
5. **Camera work**: Add smooth camera movement for demos

---

## License Compliance

When using free assets:
1. **Check license**: CC0, CC-BY, or "Free for any use"
2. **Attribution**: If CC-BY, add credit in your project README
3. **Modifications**: Most free licenses allow modification
4. **Example attribution**:
   ```
   Robot Arm Model: "Industrial Arm" by Artist Name (Sketchfab)
   License: CC Attribution (https://creativecommons.org/licenses/by/4.0/)
   ```

---

## Example Before/After

**Before**:
- 3 Unity cylinders
- 1 cube
- Default gray material
- Flat lighting

**After**:
- Professional robot arm model
- Realistic metal materials with reflections
- Textured gripper with details
- 3-point lighting setup
- Industrial environment

**Visual Impact**: 10x more professional, publication-ready

---

## Questions?

See also:
- `unity/README_Unity_Setup.md` - Basic Unity setup
- `docs/TOOLS.md` - Alternative visualization tools
- Unity Manual: https://docs.unity3d.com/Manual/ImportingAssets.html
