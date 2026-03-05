from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sympy import (
    symbols, solve, diff, integrate,
    simplify, factor, expand,
    sympify, latex
)
from sympy.parsing.latex import parse_latex
from PIL import Image
import io

# ── App init ──────────────────────────────────────────
app = FastAPI(title="Smart Math Solver API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load OCR model once at startup ────────────────────
# (downloads ~300MB weights on very first run — wait for it)
from pix2tex.cli import LatexOCR
ocr_model = LatexOCR()


# ── Request schema ────────────────────────────────────
class MathQuery(BaseModel):
    expression: str
    variable: str = "x"
    operation: str = "solve"   # solve | diff | integrate | simplify | factor


# ── Health check ──────────────────────────────────────
@app.get("/")
def root():
    return {"message": "✅ Math Solver API is running!"}


# ── Main solver endpoint ──────────────────────────────
@app.post("/compute")
def compute(query: MathQuery):
    try:
        x = symbols(query.variable)
        expr = sympify(query.expression)

        steps = []
        steps.append(f"Input Expression: {expr}")
        steps.append(f"Expanded Form: {expand(expr)}")

        if query.operation == "solve":
            result = solve(expr, x)
            steps.append(f"Factored Form: {factor(expr)}")
            steps.append(f"Solutions: {result}")

        elif query.operation == "diff":
            result = diff(expr, x)
            steps.append(f"Derivative w.r.t {query.variable}: {result}")
            steps.append(f"Simplified: {simplify(result)}")

        elif query.operation == "integrate":
            result = integrate(expr, x)
            steps.append(f"Indefinite Integral: {result} + C")

        elif query.operation == "simplify":
            result = simplify(expr)
            steps.append(f"Simplified Result: {result}")

        elif query.operation == "factor":
            result = factor(expr)
            steps.append(f"Factored Result: {result}")

        else:
            return {"error": "Invalid operation. Use: solve, diff, integrate, simplify, factor"}

        return {
            "result": str(result),
            "latex": latex(result),
            "steps": steps
        }

    except Exception as e:
        return {"error": str(e)}


# ── OCR endpoint (image → LaTeX detection only) ───────
@app.post("/ocr")
async def ocr_equation(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        latex_detected = ocr_model(image)

        return {
            "latex_detected": latex_detected,
            "message": "Equation detected! Auto-filled in solver."
        }

    except Exception as e:
        return {"error": str(e)}


# ── OCR + Auto Solve endpoint ─────────────────────────
@app.post("/ocr-and-solve")
async def ocr_and_solve(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")

        # Step 1: Image → LaTeX
        latex_detected = ocr_model(image)

        # Step 2: LaTeX → SymPy expression
        x = symbols('x')
        sympy_expr = parse_latex(latex_detected)

        # Step 3: Solve
        result = solve(sympy_expr, x)

        return {
            "latex_detected": latex_detected,
            "sympy_expression": str(sympy_expr),
            "result": str(result),
            "result_latex": latex(result)
        }

    except Exception as e:
        return {"error": str(e)}
