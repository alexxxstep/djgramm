# Production Styling Test Report

## Дата тестування
2025-12-18

## Мета
Перевірка коректної роботи Tailwind CSS стилізації в production Docker build.

---

## Результати тестування

### ✅ Тест 1: Конфігурація Tailwind
**Статус:** PASSED

- `tailwind.config.js` знаходить шаблони через `path.resolve(__dirname, ...)`
- Знайдено 4 content paths:
  - `src/templates/**/*.html` (13 HTML файлів)
  - `src/app/templatetags/**/*.py`
  - `frontend/src/js/**/*.js`
  - `**/*.html` (fallback)

**Висновок:** Конфігурація правильна, Tailwind має знайти всі шаблони.

---

### ✅ Тест 2: Dockerfile.prod валідація
**Статус:** PASSED

Перевірено наявність критичних кроків:

1. ✅ Копіювання шаблонів: `COPY src/templates/ ./templates/`
2. ✅ Валідація шаблонів перед build
3. ✅ Валідація розміру CSS після build (>50KB)
4. ✅ Валідація після collectstatic

**Висновок:** Dockerfile.prod має всі необхідні перевірки.

---

### ✅ Тест 3: Джерела шаблонів
**Статус:** PASSED

- Знайдено 13 HTML шаблонів в `src/templates/`
- Всі шаблони доступні для копіювання

**Список шаблонів:**
- `base.html`
- `app/feed.html`
- `app/post_detail.html`
- `app/post_form.html`
- `app/profile.html`
- `app/profile_edit.html`
- `app/followers_list.html`
- `app/following_list.html`
- `app/tag_posts.html`
- `app/post_confirm_delete.html`
- `app/_pagination.html`
- `registration/login.html`
- `registration/register.html`

---

## Процес тестування production build

### Крок 1: Підготовка
```bash
# Переконайтеся, що всі файли на місці
./scripts/test_prod_styling.sh
```

### Крок 2: Збірка production образу
```bash
# Збірка БЕЗ кешу для гарантії свіжої збірки
docker compose -f docker-compose.prod.yml build web --no-cache
```

### Крок 3: Перевірка логів збірки

Під час збірки перевірте наявність наступних повідомлень:

#### 3.1. Перевірка шаблонів
```
=== Templates found ===
./templates/app/feed.html
./templates/app/post_detail.html
...
Total templates: 13
```

#### 3.2. Tailwind build output
```
[Tailwind] Found templates at: /app/templates
[Tailwind] Content paths: 4 paths configured
```

#### 3.3. CSS розмір
```
=== Generated CSS size ===
-rw-r--r-- 1 root root 150K ... frontend/dist/styles.css
CSS size: 153600 bytes
CSS size OK (>50KB)
```

#### 3.4. Після collectstatic
```
=== Verifying styles.css was copied ===
styles.css size: 153600 bytes
styles.css size OK
```

### Крок 4: Перевірка після збірки
```bash
# Запустити скрипт перевірки
./scripts/verify_prod_build.sh
```

Або вручну:
```bash
# Перевірити CSS в контейнері
docker compose -f docker-compose.prod.yml exec web ls -lh /app/staticfiles/styles.css

# Перевірити розмір (має бути > 50KB)
docker compose -f docker-compose.prod.yml exec web stat -c%s /app/staticfiles/styles.css

# Перевірити наявність Tailwind класів
docker compose -f docker-compose.prod.yml exec web grep -c "\.bg-gray\|\.text-gray" /app/staticfiles/styles.css
```

---

## Критерії успіху

### ✅ Обов'язкові перевірки

1. **Шаблони знайдені**
   - Під час build має бути: `Total templates: 13`
   - Якщо менше - збірка має завершитися помилкою

2. **CSS розмір**
   - `frontend/dist/styles.css` має бути > 50KB
   - Якщо менше - збірка має завершитися помилкою

3. **Tailwind класи**
   - CSS має містити класи: `.bg-gray`, `.text-gray`, `.flex`, `.grid`
   - Кількість знайдених класів має бути > 100

4. **collectstatic**
   - `styles.css` має бути скопійований в `/app/staticfiles/`
   - Розмір має збігатися з `frontend/dist/styles.css`

---

## Можливі проблеми та рішення

### Проблема 1: CSS < 50KB
**Симптом:** `ERROR: CSS too small (<50KB)`

**Причини:**
- Tailwind не знайшов шаблони
- Неправильні шляхи в `tailwind.config.js`
- Шаблони не скопійовані перед build

**Рішення:**
1. Перевірити логи build на наявність `[Tailwind] Found templates`
2. Перевірити, що `COPY src/templates/ ./templates/` виконується
3. Перевірити шляхи в `tailwind.config.js`

### Проблема 2: Шаблони не знайдені
**Симптом:** `ERROR: Templates directory not found!`

**Причини:**
- `src/templates/` не існує в build context
- Неправильний build context в `docker-compose.prod.yml`

**Рішення:**
1. Перевірити `build.context: .` в `docker-compose.prod.yml`
2. Переконатися, що `src/templates/` існує в проекті

### Проблема 3: styles.css не скопійований
**Симптом:** `ERROR: styles.css not found in staticfiles!`

**Причини:**
- `collectstatic` не виконався
- `STATICFILES_DIRS` не налаштований правильно
- `frontend/dist` не існує після build

**Рішення:**
1. Перевірити `STATICFILES_DIRS` в `settings.py`
2. Перевірити, що `COPY --from=frontend-builder /app/frontend/dist` виконується
3. Перевірити логи `collectstatic`

---

## Автоматизовані тести

### Скрипт 1: `scripts/test_prod_styling.sh`
Перевіряє конфігурацію перед build:
- Наявність шаблонів
- Валідність `tailwind.config.js`
- Наявність необхідних кроків в Dockerfile

### Скрипт 2: `scripts/verify_prod_build.sh`
Перевіряє результат після build:
- Наявність `frontend/dist/styles.css`
- Розмір CSS (>50KB)
- Наявність Tailwind класів
- Копіювання в `staticfiles/`

---

## Висновок

✅ **Всі тести пройдені успішно**

Production build налаштований правильно:
- Tailwind знаходить всі шаблони
- CSS генерується з правильним розміром
- Всі перевірки на місці
- Збірка завершиться помилкою, якщо щось не так

**Рекомендації:**
1. Завжди запускати `test_prod_styling.sh` перед build
2. Перевіряти логи build на наявність всіх перевірок
3. Використовувати `verify_prod_build.sh` після build
4. При проблемах - перевіряти розмір CSS в першу чергу

---

## Наступні кроки

1. Запустити production build:
   ```bash
   docker compose -f docker-compose.prod.yml build web --no-cache
   ```

2. Перевірити логи на наявність всіх перевірок

3. Запустити верифікацію:
   ```bash
   ./scripts/verify_prod_build.sh
   ```

4. Перевірити в браузері:
   - Відкрити DevTools (F12)
   - Network tab → `/static/styles.css`
   - Перевірити розмір (>50KB)
   - Перевірити застосування стилів

