using UnityEngine;
using UnityEditor;

public class SceneBuilder : MonoBehaviour
{
    [MenuItem("DigitalTwin/Setup Robot Arm Scene")]
    static void SetupArm()
    {
        // Cleanup old
        GameObject old = GameObject.Find("RobotArm");
        if (old != null) DestroyImmediate(old);

        // 1. Root
        GameObject robot = new GameObject("RobotArm");
        
        // 2. Base Pedestal (Static)
        GameObject baseObj = GameObject.CreatePrimitive(PrimitiveType.Cube);
        baseObj.name = "BasePedestal";
        baseObj.transform.parent = robot.transform;
        baseObj.transform.position = new Vector3(0, -0.25f, 0);
        baseObj.transform.localScale = new Vector3(0.5f, 0.5f, 0.5f);
        
        // 3. Link 1 System
        GameObject link1Pivot = new GameObject("Link1_Pivot");
        link1Pivot.transform.parent = robot.transform;
        link1Pivot.transform.localPosition = Vector3.zero;
        
        // Shoulder Joint Visual (Sphere)
        GameObject shoulderVis = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        shoulderVis.transform.parent = link1Pivot.transform;
        shoulderVis.transform.localPosition = Vector3.zero;
        shoulderVis.transform.localScale = Vector3.one * 0.4f;

        // Link 1 Visual (Arm)
        GameObject link1Vis = GameObject.CreatePrimitive(PrimitiveType.Cube);
        link1Vis.transform.parent = link1Pivot.transform;
        // Position along X (Length 1) -> Center at 0.5
        link1Vis.transform.localPosition = new Vector3(0.5f, 0, 0); 
        link1Vis.transform.localScale = new Vector3(1.0f, 0.2f, 0.2f); // Length 1
        
        // 4. Link 2 System
        GameObject link2Pivot = new GameObject("Link2_Pivot");
        link2Pivot.transform.parent = link1Pivot.transform;
        link2Pivot.transform.localPosition = new Vector3(1.0f, 0, 0); // End of Link 1
        
        // Elbow Joint Visual (Sphere)
        GameObject elbowVis = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        elbowVis.transform.parent = link2Pivot.transform;
        elbowVis.transform.localPosition = Vector3.zero;
        elbowVis.transform.localScale = Vector3.one * 0.3f;
        
        // Link 2 Visual (Forearm)
        GameObject link2Vis = GameObject.CreatePrimitive(PrimitiveType.Cube);
        link2Vis.transform.parent = link2Pivot.transform;
        link2Vis.transform.localPosition = new Vector3(0.5f, 0, 0); 
        link2Vis.transform.localScale = new Vector3(1.0f, 0.15f, 0.15f); // Tapered slightly

        // 5. Hand / Gripper System
        GameObject handPivot = new GameObject("Hand_Pivot");
        handPivot.transform.parent = link2Pivot.transform;
        handPivot.transform.localPosition = new Vector3(1.0f, 0, 0); // End of Link 2
        
        // Wrist Visual
        GameObject wristVis = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        wristVis.transform.parent = handPivot.transform;
        wristVis.transform.localPosition = Vector3.zero;
        wristVis.transform.localScale = Vector3.one * 0.2f;
        
        // Palm/Base of Hand (Fixed)
        GameObject palm = GameObject.CreatePrimitive(PrimitiveType.Cube);
        palm.transform.parent = handPivot.transform;
        palm.transform.localPosition = new Vector3(0.1f, 0, 0); // Stick out slightly
        palm.transform.localScale = new Vector3(0.2f, 0.25f, 0.1f);
        
        // Fingers (Moving parts)
        // We'll move them along local Y (Up/Down) since palm is scaled along Y
        GameObject f1 = GameObject.CreatePrimitive(PrimitiveType.Cube);
        f1.name = "FingerUpper";
        f1.transform.parent = handPivot.transform;
        f1.transform.localScale = new Vector3(0.2f, 0.05f, 0.05f);
        // Initial pos (Open)
        f1.transform.localPosition = new Vector3(0.2f, 0.08f, 0); 

        GameObject f2 = GameObject.CreatePrimitive(PrimitiveType.Cube);
        f2.name = "FingerLower";
        f2.transform.parent = handPivot.transform;
        f2.transform.localScale = new Vector3(0.2f, 0.05f, 0.05f);
        f2.transform.localPosition = new Vector3(0.2f, -0.08f, 0); 
        
        // 6. Setup Client
        RobotArmTelemetryClient client = robot.AddComponent<RobotArmTelemetryClient>();
        client.joint1 = link1Pivot.transform;
        client.joint2 = link2Pivot.transform;
        client.axis1 = Vector3.forward; // Rotate Z
        client.axis2 = Vector3.forward;
        
        // Setup Gripper Links
        client.finger1 = f1.transform;
        client.finger2 = f2.transform;
        
        // We need to set the open/closed positions relative to the HAND PIVOT
        // Note: The client script I wrote assumes symmetric movement along X.
        // But here I built them moving along Y (Upper/Lower).
        // I need to be careful.
        
        // Let's adjust the SceneBuilder to orient the hand such that Fingers move along X?
        // OR adjust Client to move along Y?
        // Adjusting Client is harder (need to specify axis).
        // Adjusting Scene is easier: Rotate Hand Pivot so local X is "Up/Down"?
        // Or just build fingers along X.
        
        // Let's build fingers along X (Left/Right pinch).
        // Rotate Palm 90 deg around X?
        palm.transform.localRotation = Quaternion.Euler(90, 0, 0); 
        
        // Fingers move +/- Z? No, local X.
        // Let's just update the Client to assume we assign open/closed logic manually?
        // Or just make the Client simpler: Moves along LOCAL X.
        // So I should place fingers along X.
        
        // Re-doing Finger Placement:
        // Palm is at X=0.1.
        // Fingers should be at X=0.2, separated by Y.
        // Wait, Client script logic:
        // finger1.localPosition = new Vector3(pos, 0, 0);
        // This forces Y/Z to 0. That's bad if I want them offset.
        
        // Hack: Create "Finger Mounts" (empty) that are positioned correctly, and move THOSE?
        // Or update Client to use localPosition.y = initialY?
        
        // Simplest: Make fingers move along X.
        // Palm is centered.
        // Finger 1 at X=+Offset. Finger 2 at X=-Offset.
        // They pinch towards X=0.
        // This means the hand is "sideways". That's fine.
        
        f1.transform.localPosition = new Vector3(0.08f, 0, 0); // Top finger (in local space)
        f2.transform.localPosition = new Vector3(-0.08f, 0, 0); // Bottom finger
        
        // Align them to stick OUT (Length along Z?)
        // Standard cube is 1x1x1.
        // We want them long "forward".
        f1.transform.localScale = new Vector3(0.02f, 0.05f, 0.2f); 
        f2.transform.localScale = new Vector3(0.02f, 0.05f, 0.2f);
        
        // This means the hand grabs things along the Z axis?
        // Okay.
        
        // Client Script expects: finger1 moves to +pos, finger2 moves to -pos.
        // So Open = 0.08. Closed = 0.02.
        
        client.gripperOpenOffset = 0.08f;
        client.gripperClosedOffset = 0.02f;
        
        // 7. Camera
        GameObject cam = GameObject.Find("Main Camera");
        if (cam != null)
        {
            cam.transform.position = new Vector3(1.0f, 0.5f, -3.5f); // Angled view
            cam.transform.LookAt(new Vector3(1.0f, 0, 0));
        }

        Debug.Log("Robot Arm (Realistic) Setup Complete!");
    }
}
