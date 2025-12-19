using UnityEngine;
using UnityEditor;

public class SceneBuilder : MonoBehaviour
{
    [MenuItem("DigitalTwin/Setup Robot Arm Scene")]
    static void SetupArm()
    {
        // Cleanup
        GameObject old = GameObject.Find("RobotArm");
        if (old != null) DestroyImmediate(old);
        GameObject oldC = GameObject.Find("CargoBox");
        if (oldC != null) DestroyImmediate(oldC);

        // 1. Robot Root
        GameObject robot = new GameObject("RobotArm");
        
        // 2. Base (Fixed)
        GameObject baseVis = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        baseVis.transform.parent = robot.transform;
        baseVis.transform.localScale = new Vector3(1.0f, 0.1f, 1.0f); // Base plate
        baseVis.transform.localPosition = new Vector3(0, 0.1f, 0);
        
        // 3. Joint 1 (Turret - Rotates Y)
        GameObject j1 = new GameObject("Joint1_Turret");
        j1.transform.parent = robot.transform;
        j1.transform.localPosition = new Vector3(0, 0.2f, 0); // Sit on base
        
        GameObject turretVis = GameObject.CreatePrimitive(PrimitiveType.Cube);
        turretVis.transform.parent = j1.transform;
        turretVis.transform.localPosition = new Vector3(0, 0.2f, 0);
        turretVis.transform.localScale = new Vector3(0.4f, 0.4f, 0.4f);
        
        // 4. Joint 2 (Shoulder - Rotates X)
        GameObject j2 = new GameObject("Joint2_Shoulder");
        j2.transform.parent = j1.transform;
        j2.transform.localPosition = new Vector3(0, 0.4f, 0); // Top of turret
        
        // Arm Link (Extends Up Y)
        GameObject armVis = GameObject.CreatePrimitive(PrimitiveType.Cube);
        armVis.transform.parent = j2.transform;
        armVis.transform.localPosition = new Vector3(0, 0.75f, 0); // Center at 0.75
        armVis.transform.localScale = new Vector3(0.3f, 1.5f, 0.3f); // Length 1.5, Thicker
        
        // 5. Joint 3 (Elbow - Rotates X)
        GameObject j3 = new GameObject("Joint3_Elbow");
        j3.transform.parent = j2.transform;
        j3.transform.localPosition = new Vector3(0, 1.5f, 0); // End of Arm (1.5)
        
        GameObject elbowVis = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        elbowVis.transform.parent = j3.transform;
        elbowVis.transform.localScale = Vector3.one * 0.4f;
        
        // Forearm Link (Extends Up Y)
        GameObject forearmVis = GameObject.CreatePrimitive(PrimitiveType.Cube);
        forearmVis.transform.parent = j3.transform;
        forearmVis.transform.localPosition = new Vector3(0, 0.75f, 0); // Center at 0.75
        forearmVis.transform.localScale = new Vector3(0.25f, 1.5f, 0.25f); // Length 1.5, Thicker
        
        // 6. Wrist/Hand
        GameObject handPivot = new GameObject("Wrist");
        handPivot.transform.parent = j3.transform;
        handPivot.transform.localPosition = new Vector3(0, 1.5f, 0); // End of Forearm (1.5)
        
        // Palm
        GameObject palm = GameObject.CreatePrimitive(PrimitiveType.Cube);
        palm.transform.parent = handPivot.transform;
        palm.transform.localPosition = new Vector3(0, 0.1f, 0);
        palm.transform.localScale = new Vector3(0.2f, 0.2f, 0.1f);
        
        // Fingers (Moving along X)
        GameObject f1 = GameObject.CreatePrimitive(PrimitiveType.Cube);
        f1.name = "FingerL";
        f1.transform.parent = handPivot.transform;
        f1.transform.localScale = new Vector3(0.02f, 0.2f, 0.05f);
        f1.transform.localPosition = new Vector3(0.08f, 0.2f, 0);
        
        GameObject f2 = GameObject.CreatePrimitive(PrimitiveType.Cube);
        f2.name = "FingerR";
        f2.transform.parent = handPivot.transform;
        f2.transform.localScale = new Vector3(0.02f, 0.2f, 0.05f);
        f2.transform.localPosition = new Vector3(-0.08f, 0.2f, 0);
        
        // 7. Cargo Box
        GameObject cargo = GameObject.CreatePrimitive(PrimitiveType.Cube);
        cargo.name = "CargoBox";
        cargo.transform.position = new Vector3(-1.5f, 0.2f, 0); // Moved to -1.5 (Longer reach)
        cargo.transform.localScale = Vector3.one * 0.3f;
        
        // Add a Handle
        GameObject handle = GameObject.CreatePrimitive(PrimitiveType.Cube);
        handle.name = "Handle";
        handle.transform.parent = cargo.transform;
        handle.transform.localPosition = new Vector3(0, 0.6f, 0); // Top of box
        handle.transform.localScale = new Vector3(0.4f, 0.2f, 0.4f); // Small grab point
        handle.transform.localRotation = Quaternion.identity;
        
        // 8. Configure Client
        RobotArmTelemetryClient client = robot.AddComponent<RobotArmTelemetryClient>();
        client.joint1 = j1.transform;
        client.joint2 = j2.transform;
        client.joint3 = j3.transform;
        client.cargo = cargo.transform;
        client.finger1 = f1.transform;
        client.finger2 = f2.transform;
        
        // Set Axes (Base Y, Shoulder X, Elbow X)
        client.axis1 = Vector3.up;
        client.axis2 = Vector3.right;
        client.axis3 = Vector3.right;
        
        client.gripperOpenOffset = 0.08f;
        client.gripperClosedOffset = 0.02f;
        
        // 9. Camera
        GameObject cam = GameObject.Find("Main Camera");
        if (cam != null)
        {
            cam.transform.position = new Vector3(2.5f, 2.0f, -2.5f);
            cam.transform.LookAt(new Vector3(0, 1.0f, 0));
        }
        
        Debug.Log("3D Robot Arm Scene Setup Complete!");
    }
}