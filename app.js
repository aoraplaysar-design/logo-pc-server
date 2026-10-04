const menuBtn = document.getElementById("menuBtn");
const mainNav = document.getElementById("mainNav");

menuBtn.addEventListener("click", () => {
    mainNav.classList.toggle("open");
});

document.querySelectorAll("#mainNav a").forEach(link => {
    link.addEventListener("click", () => {
        mainNav.classList.remove("open");
    });
});


/* TOAST */

function showMessage(message) {
    const toast = document.getElementById("toast");

    toast.textContent = message;
    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 2500);
}


/* CALCULATOR */

let subjectNumber = 0;

function addSubject(name = "", mark = "", coefficient = "") {

    subjectNumber++;

    const container = document.getElementById("subjects");

    const row = document.createElement("div");

    row.className = "subject";

    row.innerHTML = `
        <input
            type="text"
            class="subject-name"
            placeholder="المادة"
            value="${name}"
        >

        <input
            type="number"
            class="subject-mark"
            min="0"
            max="20"
            step="0.01"
            placeholder="النقطة /20"
            value="${mark}"
        >

        <input
            type="number"
            class="subject-coef"
            min="1"
            step="1"
            placeholder="المعامل"
            value="${coefficient}"
        >

        <button
            class="remove-subject"
            onclick="this.parentElement.remove()"
        >
            ×
        </button>
    `;

    container.appendChild(row);
}


function openCalculator() {

    document.getElementById("calculator")
        .scrollIntoView({
            behavior: "smooth"
        });

    if (document.querySelectorAll(".subject").length === 0) {
        addSubject("اللغة العربية", "", 1);
        addSubject("الرياضيات", "", 1);
        addSubject("اللغة الفرنسية", "", 1);
    }
}


function closeCalculator() {
    document.getElementById("calculator")
        .scrollIntoView({
            behavior: "smooth"
        });
}


function calculateAverage() {

    const rows = document.querySelectorAll(".subject");

    let total = 0;
    let coefficients = 0;

    rows.forEach(row => {

        const mark = parseFloat(
            row.querySelector(".subject-mark").value
        );

        const coefficient = parseFloat(
            row.querySelector(".subject-coef").value
        );

        if (
            !isNaN(mark) &&
            !isNaN(coefficient) &&
            mark >= 0 &&
            mark <= 20 &&
            coefficient > 0
        ) {
            total += mark * coefficient;
            coefficients += coefficient;
        }
    });

    const result = document.getElementById("averageResult");

    result.classList.remove("hidden");

    if (coefficients === 0) {
        result.textContent = "أدخل النقاط والمعاملات أولاً.";
        return;
    }

    const average = total / coefficients;

    result.innerHTML =
        `معدلك هو <strong>${average.toFixed(2)} / 20</strong>`;
}


/* PERCENTAGE */

function openPercentage() {

    closeUtilities();

    const tool = document.getElementById("percentageTool");

    tool.classList.remove("hidden");

    tool.parentElement.scrollIntoView({
        behavior: "smooth"
    });
}


function calculatePercentage() {

    const value = parseFloat(
        document.getElementById("percentValue").value
    );

    const total = parseFloat(
        document.getElementById("percentTotal").value
    );

    const result = document.getElementById("percentResult");

    if (
        isNaN(value) ||
        isNaN(total) ||
        total === 0
    ) {
        result.textContent = "أدخل قيمًا صحيحة.";
        return;
    }

    const percentage = (value / total) * 100;

    result.textContent =
        `${percentage.toFixed(2)}%`;
}


/* AGE */

function openAge() {

    closeUtilities();

    const tool = document.getElementById("ageTool");

    tool.classList.remove("hidden");

    tool.parentElement.scrollIntoView({
        behavior: "smooth"
    });
}


function calculateAge() {

    const input = document.getElementById("birthDate").value;

    const result = document.getElementById("ageResult");

    if (!input) {
        result.textContent = "اختر تاريخ الميلاد.";
        return;
    }

    const birth = new Date(input);
    const today = new Date();

    let years =
        today.getFullYear() -
        birth.getFullYear();

    let months =
        today.getMonth() -
        birth.getMonth();

    let days =
        today.getDate() -
        birth.getDate();

    if (days < 0) {
        months--;
    }

    if (months < 0) {
        years--;
        months += 12;
    }

    result.textContent =
        `عمرك: ${years} سنة و ${months} شهر`;
}


/* TEXT COUNTER */

function openTextCounter() {

    closeUtilities();

    const tool = document.getElementById("textTool");

    tool.classList.remove("hidden");

    tool.parentElement.scrollIntoView({
        behavior: "smooth"
    });
}


const textInput = document.getElementById("textInput");

textInput.addEventListener("input", updateTextStats);

function updateTextStats() {

    const text = textInput.value;

    const characters = text.length;

    const words = text.trim() === ""
        ? 0
        : text.trim().split(/\s+/).length;

    document.getElementById("charCount")
        .textContent = characters;

    document.getElementById("wordCount")
        .textContent = words;
}


function closeUtilities() {

    document
        .querySelectorAll(".utility-box")
        .forEach(box => {
            box.classList.add("hidden");
        });
}


/* DEFAULT SUBJECTS */

addSubject("اللغة العربية", "", 1);
addSubject("الرياضيات", "", 1);
