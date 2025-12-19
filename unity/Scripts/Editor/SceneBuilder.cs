using UnityEngine;
using UnityEditor;

public class SceneBuilder : MonoBehaviour
{
    [MenuItem("DigitalTwin/Setup Robot Arm Scene")]
    static void SetupArm()
    {
        // 1. Create Parent Object (The Robot)
        GameObject robot = new GameObject("RobotArm");
        
        // 2. Create Joint 1 (Base/Shoulder)
        GameObject j1 = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        j1.name = "Joint1";
        j1.transform.parent = robot.transform;
        j1.transform.localPosition = Vector3.zero;
        j1.transform.localRotation = Quaternion.identity;
        // Make it look like a limb (long Y axis)
        j1.transform.localScale = new Vector3(0.2f, 1.0f, 0.2f);
        
        // 3. Create Joint 2 (Elbow) - Child of Joint 1?
        // Actually, for a simple visualization, Joint 2 should be at the TIP of Joint 1.
        // A cylinder is 2 units high (center at 0, goes from -1 to 1).
        // So tip is at Y=1.
        
        GameObject j2 = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        j2.name = "Joint2";
        j2.transform.parent = j1.transform;
        // Position at the top of J1
        j2.transform.localPosition = new Vector3(0, 1.0f, 0); 
        // We want J2 to rotate relative to J1. 
        // But visually, we want J2 to start *after* J1.
        // And we want the pivot to be at the connection point.
        // The cylinder pivot is in the CENTER. This makes rotation tricky visually without a pivot object.
        
        // Let's do it properly: Pivot objects.
        DestroyImmediate(j1);
        DestroyImmediate(j2);
        DestroyImmediate(robot);
        
        robot = new GameObject("RobotArm");
        
        // --- Link 1 ---
        GameObject link1Pivot = new GameObject("Link1_Pivot");
        link1Pivot.transform.parent = robot.transform;
        link1Pivot.transform.localPosition = Vector3.zero;
        
        GameObject link1Vis = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        link1Vis.transform.parent = link1Pivot.transform;
        link1Vis.transform.localPosition = new Vector3(0, 0.5f, 0); // Move up so pivot is at base
        link1Vis.transform.localScale = new Vector3(0.1f, 0.5f, 0.1f); // 1 unit long
        link1Vis.transform.localRotation = Quaternion.Euler(0, 0, 90); // Lay flat along X?
        // Let's stick to the Python model:
        // q1 is angle from X axis.
        // So at q1=0, it points along X.
        // Default Cylinder points along Y.
        link1Vis.transform.localRotation = Quaternion.Euler(0, 0, -90); // Point along X
        
        // --- Link 2 ---
        GameObject link2Pivot = new GameObject("Link2_Pivot");
        link2Pivot.transform.parent = link1Pivot.transform;
        link2Pivot.transform.localPosition = new Vector3(1.0f, 0, 0); // At end of Link 1 (length=1)
        
        GameObject link2Vis = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        link2Vis.transform.parent = link2Pivot.transform;
        link2Vis.transform.localPosition = new Vector3(0.5f, 0, 0); // Center at 0.5 (length=1)
        link2Vis.transform.localScale = new Vector3(0.1f, 0.5f, 0.1f);
        link2Vis.transform.localRotation = Quaternion.Euler(0, 0, -90); // Point along X
        
        // 4. Attach Client
        RobotArmTelemetryClient client = robot.AddComponent<RobotArmTelemetryClient>();
        client.joint1 = link1Pivot.transform;
        client.joint2 = link2Pivot.transform;
        client.axis1 = Vector3.forward; // Rotate around Z
        client.axis2 = Vector3.forward;
        
        // 5. Camera Setup
        GameObject cam = GameObject.Find("Main Camera");
        if (cam != null)
        {
            cam.transform.position = new Vector3(0, 0, -5);
            cam.transform.LookAt(Vector3.zero);
        }
        
        Debug.Log("Robot Arm Scene Setup Complete!");
    }
}
