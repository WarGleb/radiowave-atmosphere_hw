# ДЗ-1. Лист справки

Запись проницаемости в задании: $\hat\varepsilon = \varepsilon' - j\varepsilon''$, поле $\propto e^{j\omega t}$, потери дают $\varepsilon'' > 0$. Раздел «Для сверки» открывайте после того, как вывели формулу сами.

### [1, §18, с. 91–92, ф. (66)–(67)]

**О чём.** Комплексная проницаемость среды с одним временем релаксации. У Дебая время входит в безразмерной частоте $x = \dfrac{\varepsilon_1 + 2}{\varepsilon_0 + 2}\,\omega\tau$, где $\varepsilon_0$ — статическая проницаемость, $\varepsilon_1$ — высокочастотная. В задании поправку на внутреннее поле не учитываем: $x = \omega\tau$.

**Для сверки.**

$$\varepsilon' = \varepsilon_{вч} + \frac{\Delta\varepsilon}{1 + x^2}, \qquad \varepsilon'' = \frac{\Delta\varepsilon\, x}{1 + x^2}, \qquad \Delta\varepsilon = \varepsilon_{ст} - \varepsilon_{вч}.$$

В коде: `eps = eps_inf + d_eps / (1 + 1j*w*tau)`. Мнимая часть этого числа равна $-\varepsilon''$, поэтому $\varepsilon''$ берите как `-eps.imag`.

### [2, §7.5А, с. 309, ф. (7.49)]

**О чём.** Модель Лоренца: связанный заряд (электрон в атоме или молекуле) с массой $m$, зарядом $-e$, собственной частотой $\omega_0$ и затуханием $\gamma$ в поле волны.

**Для вывода.** Уравнение движения смещения $x$ заряда:

$$m\,(\ddot x + \gamma\dot x + \omega_0^2 x) = -e E.$$

Поляризация $P = -N e x$, откуда $\hat\varepsilon = 1 + P/(\varepsilon_0 E)$. Подставьте $E \propto e^{j\omega t}$.

**Для сверки.** Для $N$ одинаковых зарядов:

$$\hat\varepsilon(\omega) = 1 + \frac{\omega_p^2}{\omega_0^2 - \omega^2 + j\omega\gamma}, \qquad \omega_p^2 = \frac{N e^2}{\varepsilon_0 m}.$$

Если зарядов нескольких сортов, под знак суммы входят силы осцилляторов $f_j$. В задании один осциллятор, а его сила задана числом $\Delta\varepsilon$ через $\omega_p^2 = \Delta\varepsilon\,\omega_0^2$. Тогда $\hat\varepsilon = 1 + \dfrac{\Delta\varepsilon\,\omega_0^2}{\omega_0^2 - \omega^2 + j\omega\gamma}$, где $\gamma = \nu = 2\pi\,\Delta f_L$.

### [2, с. 311–312, ф. (7.56)]

**О чём.** Свободные электроны: предел модели Лоренца при $\omega_0 = 0$ (нет возвращающей силы), $\gamma$ становится частотой соударений $\nu$.

**Для сверки.**

$$\hat\varepsilon(\omega) = 1 - \frac{\omega_p^2}{\omega^2 - j\omega\nu}.$$

Разделив на действительную и мнимую части (в задании $\tan\delta = \varepsilon''/|\varepsilon'|$), получите $\varepsilon' = 1 - \dfrac{\omega_p^2}{\omega^2 + \nu^2}$ и $\varepsilon'' = \dfrac{\omega_p^2\,\nu}{\omega\,(\omega^2 + \nu^2)}$.

### [2, с. 313, ф. (7.60)]

**О чём.** Плазменная частота электронного газа.

**Для сверки.**

$$\omega_p^2 = \frac{N e^2}{\varepsilon_0 m_e}, \qquad f_p = \frac{\omega_p}{2\pi}.$$

Удобный вид для оценок: $f_p \approx 8{,}98\,\sqrt{N}$ Гц при $N$ в м⁻³.

### [2, с. 316, ф. (7.63)]

**О чём.** Соглашение о знаке. Джексон записывает поле как $e^{-i\omega t}$, поэтому у него потери дают $\varepsilon'' > 0$ при записи $\varepsilon' + i\varepsilon''$. В задании поле $e^{j\omega t}$ и запись $\varepsilon' - j\varepsilon''$.

**Для перевода.** Замените $i \to -j$ в формулах Джексона. Тогда $-i\omega\gamma$ превращается в $+j\omega\gamma$, а $\varepsilon''$ остаётся положительным. Если у вас получился отрицательный $\varepsilon''$, знак перед $j$ выбран не тот.
