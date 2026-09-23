const form = document.getElementById("my-form");
const status = document.getElementById("my-form-status");
const submitButton = document.getElementById("my-form-button");

const contactConfig = window.SITE_CONTACT || {};
const DISPLAY_EMAIL =
  contactConfig.displayEmail || "junye.zhou@mail.utoronto.ca";
const WEB3FORMS_KEY = (contactConfig.web3formsAccessKey || "").trim();
const WEB3FORMS_URL = "https://api.web3forms.com/submit";

function setStatus(message, type) {
  if (!status) return;
  status.textContent = message;
  status.classList.remove("is-success", "is-error", "is-sending");
  if (type) status.classList.add(type);
}

function openMailto(email, message) {
  const subject = "Message from Junye portfolio";
  const body = `From: ${email}\n\n${message}`;
  window.location.href = `mailto:${DISPLAY_EMAIL}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
}

function web3formsSucceeded(data) {
  return data && data.success === true;
}

if (form && status) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const honey = form.querySelector('input[name="_honey"]');
    if (honey && honey.value.trim()) {
      setStatus("", null);
      form.reset();
      return;
    }

    const email = form.email?.value?.trim() || "";
    const message = form.message?.value?.trim() || "";

    if (!email || !message) {
      setStatus("Failed to send. Fill in both fields.", "is-error");
      return;
    }

    const originalLabel = submitButton ? submitButton.textContent : "";

    if (submitButton) {
      submitButton.disabled = true;
      submitButton.textContent = "Sending…";
    }
    setStatus("Sending…", "is-sending");

    if (!WEB3FORMS_KEY) {
      openMailto(email, message);
      setStatus(
        "Opening your email app — tap Send there to deliver your message.",
        "is-success"
      );
      if (submitButton) {
        submitButton.disabled = false;
        submitButton.textContent = originalLabel;
      }
      return;
    }

    try {
      const response = await fetch(WEB3FORMS_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          access_key: WEB3FORMS_KEY,
          email,
          message,
          subject: "New message from Junye portfolio",
          from_name: "Portfolio visitor",
          replyto: email,
        }),
      });

      const data = await response.json();

      if (web3formsSucceeded(data)) {
        setStatus("Email sent.", "is-success");
        form.reset();
        return;
      }

      throw new Error(data.message || "Rejected");
    } catch {
      setStatus(
        `Failed to send. Use the email link above or try again.`,
        "is-error"
      );
    } finally {
      if (submitButton) {
        submitButton.disabled = false;
        submitButton.textContent = originalLabel;
      }
    }
  });
}
