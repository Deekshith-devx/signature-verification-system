import os
import pandas as pd
from flask import Flask, request, render_template, redirect, url_for, session, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from signature_matcher import compare_signatures

app = Flask(__name__)
app.secret_key = "super_secret_admin_signature_key_2026"
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")
app.config["DATABASE_FOLDER"] = os.path.join("database", "signatures")

# Ensure upload directory exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def is_admin_logged_in():
    return session.get("logged_in") == True

@app.route("/")
def index():
    if is_admin_logged_in():
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if is_admin_logged_in():
        return redirect(url_for("dashboard"))
        
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid admin credentials."
            
    return render_template("login.html", error=error)

@app.route("/dashboard")
def dashboard():
    if not is_admin_logged_in():
        return redirect(url_for("login"))
    return render_template("dashboard.html")

@app.route("/verify", methods=["POST"])
def verify():
    if not is_admin_logged_in():
        return jsonify({"success": False, "message": "Unauthorized access."}), 401
        
    uid = request.form.get("uid")
    if not uid:
        return jsonify({"success": False, "message": "User ID is required."})
        
    if "signature" not in request.files:
        return jsonify({"success": False, "message": "Signature image is required."})
        
    file = request.files["signature"]
    if file.filename == "":
        return jsonify({"success": False, "message": "No file selected."})
        
    # Read database CSV
    csv_path = os.path.join("database", "signatures.csv")
    if not os.path.exists(csv_path):
        return jsonify({"success": False, "message": "Database not initialized. Please run generate_dataset.py."})
        
    df = pd.read_csv(csv_path)
    
    # Cast ID to string for matching
    df["id"] = df["id"].astype(str).str.strip()
    uid = str(uid).strip()
    
    # 1. Check if the unique number is valid (exists in the CSV)
    user_record = df[df["id"] == uid]
    if user_record.empty:
        # If unique number is not valid, give the error message: "user id or signature not matching"
        return jsonify({
            "success": False, 
            "message": "user id or signature not matching",
            "reason": "User ID not found in database"
        })
        
    # User is valid, get reference signature details
    user_name = user_record.iloc[0]["name"]
    ref_sig_path = user_record.iloc[0]["signature_path"]
    
    # Check if reference signature file exists
    if not os.path.exists(ref_sig_path):
        return jsonify({
            "success": False,
            "message": "Reference signature image not found on server.",
            "reason": f"File {ref_sig_path} does not exist"
        })
        
    # Save uploaded file temporarily
    filename = secure_filename(f"upload_{uid}_{file.filename}")
    upload_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(upload_path)
    
    # Generate path for comparison visualization
    comparison_filename = f"compare_{uid}.png"
    comparison_path = os.path.join(app.config["UPLOAD_FOLDER"], comparison_filename)
    
    # 2. Compare uploaded signature with reference signature
    score, is_match, details = compare_signatures(ref_sig_path, upload_path, debug_out_path=comparison_path)
    
    # Clean up the raw uploaded temp file
    if os.path.exists(upload_path):
        try:
            os.remove(upload_path)
        except Exception:
            pass
            
    # Result message formatting
    if is_match:
        return jsonify({
            "success": True,
            "message": "Signature verified successfully!",
            "details": details,
            "user_name": user_name,
            "user_id": uid,
            "comparison_url": f"/static/uploads/{comparison_filename}?t={os.urandom(4).hex()}",
            "ref_url": f"/database/signatures/{uid}.png"
        })
    else:
        # If valid but signature does not match, return: "user id or signature not matching"
        return jsonify({
            "success": False,
            "message": "user id or signature not matching",
            "reason": f"Signature match score too low ({details.get('combined_score', 0)}%)",
            "details": details,
            "user_id": uid,
            "comparison_url": f"/static/uploads/{comparison_filename}?t={os.urandom(4).hex()}" if os.path.exists(comparison_path) else None
        })

@app.route("/register", methods=["POST"])
def register():
    if not is_admin_logged_in():
        return jsonify({"success": False, "message": "Unauthorized access."}), 401
        
    uid = request.form.get("uid")
    name = request.form.get("name")
    
    if not uid or not name:
        return jsonify({"success": False, "message": "User ID and Full Name are required."})
        
    if "signature" not in request.files:
        return jsonify({"success": False, "message": "Signature specimen image is required."})
        
    file = request.files["signature"]
    if file.filename == "":
        return jsonify({"success": False, "message": "No file selected."})
        
    # Read database CSV
    csv_path = os.path.join("database", "signatures.csv")
    
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        # Convert IDs to strings and strip whitespaces
        df["id"] = df["id"].astype(str).str.strip()
        uid_str = str(uid).strip()
        
        # Check if ID already exists
        if uid_str in df["id"].values:
            return jsonify({"success": False, "message": f"User ID {uid_str} is already registered."})
    else:
        df = pd.DataFrame(columns=["id", "name", "signature_path"])
        
    # Save new signature image
    os.makedirs(app.config["DATABASE_FOLDER"], exist_ok=True)
    filename = f"{secure_filename(str(uid).strip())}.png"
    save_path = os.path.join(app.config["DATABASE_FOLDER"], filename)
    file.save(save_path)
    
    # Add new row and write back to CSV
    rel_sig_path = f"database/signatures/{filename}"
    new_row = pd.DataFrame([{"id": str(uid).strip(), "name": name.strip(), "signature_path": rel_sig_path}])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(csv_path, index=False)
    
    return jsonify({
        "success": True,
        "message": f"User {name} (ID: {uid}) registered successfully!"
    })

@app.route("/database/signatures/<path:filename>")
def serve_db_signature(filename):
    if not is_admin_logged_in():
        return "Unauthorized", 401
    return send_from_directory(app.config["DATABASE_FOLDER"], filename)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
