# Page snapshot

```yaml
- generic [ref=e5]:
  - generic [ref=e6]:
    - generic [ref=e8]: AI
    - heading "Create your account" [level=2] [ref=e9]
    - paragraph [ref=e10]: AI Job Application Assistant
  - form "registration form" [ref=e13]:
    - generic [ref=e14]:
      - generic [ref=e15]: Full Name (Optional)
      - textbox "Full Name (Optional)" [ref=e17]:
        - /placeholder: Enter your name
    - generic [ref=e18]:
      - generic [ref=e19]: Email address*
      - textbox "Email address*" [ref=e21]:
        - /placeholder: Enter your email
    - generic [ref=e22]:
      - generic [ref=e23]: Password*
      - textbox "Password*" [ref=e25]:
        - /placeholder: Enter your password
      - paragraph [ref=e26]: Must be at least 8 characters with uppercase, lowercase, and a number
    - generic [ref=e27]:
      - generic [ref=e28]: Confirm Password*
      - textbox "Confirm Password*" [ref=e30]:
        - /placeholder: Confirm your password
    - button "Create Account" [ref=e32] [cursor=pointer]
    - paragraph [ref=e34]:
      - text: Already have an account?
      - link "Sign in" [ref=e35] [cursor=pointer]:
        - /url: /login
```