Title: Faster Division With Newton-Raphson Approximation
Date: 2025-10-04
Tags: cs

Many devices, especially embedded devices (micro-controllers and the like) do
not come with an [FPU](https://en.wikipedia.org/wiki/Floating-point_unit) and
circuitry required for carrying out integer division. In such a case, one looks
towards methods of approximating the results of division and storing them in
[Fixed Point](https://en.wikipedia.org/wiki/Fixed-point_arithmetic) format.

C has standardized support for such an instance via its stdfix library. The [ISO
Document](https://standards.iso.org/ittf/PubliclyAvailableStandards/c051126_ISO_IEC_TR_18037_2008.zip)
describes the data types and functions available in `stdfix.h`.

This post describes the theory, provides a dependency-free C++ implementation of
the core algorithm and discusses optimizations to speed it up even further. In
that order.

## Theory

The problem at hand is that of division:

```
C = N/D
```
The first step to solving this is to split the problem in two: Reciprocal
calculation, followed by multiplication. This is what it looks like:

```
C = N * (1/D)
```
It is assumed that the device has a fast multiplication hardware (which is
mostly the case). Thus, multiplication can be carried out by the good old `mul`
instruction. Now for the most tricky part - calculating the reciprocal - which
is a division operation!

As it turns out, this is a known problem and solutions are *approximately* [as
old as](http://degiorgi.math.hr/aaa_sem/Div/702-706.pdf) the [Unix
epoch](https://en.wikipedia.org/wiki/Unix_time).

### Newton-Raphson Method

The [Wikipedia
article](https://en.wikipedia.org/wiki/Division_algorithm#Newton%E2%80%93Raphson_division)
suffiecienty describes *what* and *how* of the NR Method. I'll summarize and add some
missing context to make it digestable. 

"[Newton's Method](https://en.wikipedia.org/wiki/Newton%27s_method) is a
root-finding algorithm which produces successively better approximations to the
roots (or zeroes) of a real-valued function." This is the generic iterative
equation according to Newton's method:


<h3 align="center">
<math xmlns="http://www.w3.org/1998/Math/MathML"><msub><mi>x</mi><mrow><mn>1</mn><mo>&#xA0;</mo></mrow></msub><mo>=</mo><mo>&#xA0;</mo><msub><mi>x</mi><mrow><mn>0</mn><mo>&#xA0;</mo></mrow></msub><mo>-</mo><mo>&#xA0;</mo><mfrac><mrow><mi>f</mi><mo>(</mo><msub><mi>x</mi><mn>0</mn></msub><mo>)</mo></mrow><mrow><mi>f</mi><mo>'</mo><mo>(</mo><msub><mi>x</mi><mn>0</mn></msub><mo>)</mo></mrow></mfrac><mo>&#xA0;</mo><mo>&#xA0;</mo></math>
</h3>

The idea is to find a function `f(x)` for which `x = 1/D` is zero. One such
function is:

<math xmlns="http://www.w3.org/1998/Math/MathML"><mi>f</mi><mo>(</mo><mi>x</mi><mo>)</mo><mo>&#xA0;</mo><mo>=</mo><mo>&#xA0;</mo><mo>(</mo><mn>1</mn><mo>/</mo><mi>x</mi><mo>)</mo><mo>&#xA0;</mo><mo>-</mo><mo>&#xA0;</mo><mi>D</mi></math>

(Substitue `x = 1/D` in the above equation and it should result in zero)

Next, we find `f'(x)` and substitue it in the NM equation to give us an equation
that allows successive improvements.

<h3 align="center">
<math xmlns="http://www.w3.org/1998/Math/MathML"><msub><mi>x</mi><mrow><mi>i</mi><mo>+</mo><mn>1</mn></mrow></msub><mo>&#xA0;</mo><mo>=</mo><mo>&#xA0;</mo><msub><mi>x</mi><mi>i</mi></msub><mo>-</mo><mfrac><mrow><mn>1</mn><mo>/</mo><msub><mi>x</mi><mi>i</mi></msub><mo>&#xA0;</mo><mo>-</mo><mo>&#xA0;</mo><mi>D</mi></mrow><mrow><mo>-</mo><mn>1</mn><mo>/</mo><msup><msub><mi>x</mi><mi>i</mi></msub><mn>2</mn></msup></mrow></mfrac><mo>&#xA0;</mo><mo>=</mo><msub><mi>x</mi><mi>i</mi></msub><mo>&#xA0;</mo><mo>(</mo><mn>2</mn><mo>&#xA0;</mo><mo>-</mo><mo>&#xA0;</mo><mi>D</mi><msub><mi>x</mi><mi>i</mi></msub><mo>)</mo></math>
</h3>

Astute readers will notice that the result `x₂` (result of the second iteration)
depends on `x₁` and`x₁` (result of the first iteration) depends on `x₀`. How do
we calculate `x₀`? This is the problem of initial approximation.

### Initial Approximation to the Reciprocal

Lest the curtain be drawn too soon, here's the final equation for calculating
`x₀`, provided `D` has been scaled to be in the range `[0.5,1]`

```
x₀ = 48/17 - 32/17 * D
```

We notice that the equation at hand is a **linear**, **smooth** and
**non-periodic** function. In numerical algorithms like division, the goal isn't
necessarily the smallest average error, but guaranteeing the worst−case error
(∣ε₀∣) is as small as possible. This predictability is important because the
initial error directly determines the number of Newton-Raphson iterations
required to reach full machine precision. 

We wish to calculate an approximation for this function such that the
**worst-case error** is minimal. The right tool for this job is the [Chebyshev
Equioscillation Theorem](https://en.wikipedia.org/wiki/Equioscillation_theorem). 

Chebyshev approximation is used because it provides the
Best Uniform Approximation (or Minimax Approximation). This means that out of
all possible polynomials of a given degree, the Chebyshev method yields the one
that minimizes the maximum absolute error across the entire target interval.

We start with formulating the error function on whoch equioscillation will be
applied. The error function for figuring out the reciprocal `x₀ = 1/D` using a
simple straight line `x₀ = T₀ + T₁·D` (a linear equation) tells us how far off
our guess is from the perfect answer. Because we want the total result `D·x₀` to
be near `1`, we make the error function `f(D)` measure the difference between
that product and `1`. The formula is `f(D) = 1 - D·x₀`. When we plug in the
straight-line guess, the formula becomes: 

```
f(D) = 1 - T₀·D - T₁·D²
```

The main goal is to pick the numbers `T₀` and `T₁` that make the absolute value
of this error `f(D)` as small as possible everywhere in the range. This is
exactly what the Chebyshev method does.

Before we apply the theorem on the error equation, we need to constrain the
values that `D` can take. Bounding D guarantees that the starting error is small
enough for the subsequent iterations to converge quickly and predictably to full
fixed-point precision. Without this bound, a much more complex, higher-degree
polynomial would be needed, defeating the efficiency goal. We bound `D` to be
`[0.5,1]`. In code, this scaling can be achieved through simple bit-shifts
(exemplified later in the code). As long as we scale the numerator too, we
should be good.

The theorem states that a polynomial is the best uniform approximation to a
continuous function over an interval if and only if the error function
alternates between its maximum positive and maximum negative values at least
(n+2) times, where `n` is the degree of the polynomial.

The theorem requires the maximum error to occur at the two endpoints (D=1/2 and
D=1) and the local extremum (Dmin) between them.  

The location of the local extremum is found by setting the derivative to zero:

```
F'(D) = -T0 - 2T1 D = 0, which gives:
D_min = - T0 / (2T1)
```

The first condition of the theorem is that the error magnitude is equal at
endpoints i.e. 

```
f(1/2) = f(1)

1 - T₀/2 - T₁/4 = 1 - T₀ - T₁ 
```
This simplifies to:

```
T₀ = - (3/2)·T₁
```
The second condition states that the error at endpoints must be the negative of
the error at the extremum i.e. 

```
f(1) = -f(Dmin)
1 - T0 - T1 = - (1 + T0^2 / (4T1))
```
Substituing the value of T0 from above, 

```
1 - (-3/2 * T1) - T1 = -1 - ((-3/2 * T1)^2 / (4T1))
1 + (1/2)T1 = -1 - (9T1 / 16)
```
Solving this linear equation for T1:
```
2 = -17T1 / 16 
T1 = - 32/17
```
Substituting T1 back into the original equation to find T0:
```
T0 = -(3/2) * (-32/17) 
T0 = 48/17
```

The resulting linear approximation is X0 = T0 + T1 D:

```
X0 = 48/17 - 32/17 * D
```

This equation gives us an initial estimate for the reciprocal that can be
refined by iterations of the NR equation that we found earlier.

## Implementation

(A [link](https://gist.github.com/bojle/60f9f9c0a7b0678a2f6b51553217ab6a) to the complete implementation)

The original rationale for doing this was two-fold:

1. Lack of division circuitry.
2. Lack of support for floating point types.

Lack of division circuitry has been dealt with through the design of the
algorithm above. Lack of floating point types can be dealt with by using
[Fixed-Point notation](https://en.wikipedia.org/wiki/Fixed-point_arithmetic).
Fixed point allows us to get away with storing everything in integers and
operate using bit-shift operations, which tend to be cost efficient.

Here's an implementation of a fixed point types in C++:

```
#include <iostream>
#include <cmath>
#include <cstdint>
#include <type_traits>
#include <limits>
#include <cassert>
#include <numeric>

template <int FRAC_BITS, int TOTAL_BITS>
class FixedPoint {
    using BaseType = decltype([] {
        if constexpr (TOTAL_BITS <= 8) {
            return int8_t{};
        } else if constexpr (TOTAL_BITS <= 16) {
            return int16_t{};
        } else if constexpr (TOTAL_BITS <= 32) {
            return int32_t{};
        } else {
            return int64_t{};
        }
    }());

    using WideType = typename std::conditional<(sizeof(BaseType) <= 4), int64_t, __int128_t>::type;
    BaseType value;

public:
    constexpr static BaseType SCALE = static_cast<BaseType>(1ULL << FRAC_BITS);
    FixedPoint() : value(0) {}
    FixedPoint(float f) : value(static_cast<BaseType>(std::round(f * SCALE))) {}
    BaseType raw() const { return value; }

    static FixedPoint fromRaw(BaseType rawVal) {
        FixedPoint fp;
        fp.value = rawVal;
        return fp;
    }

    float toFloat() const { return static_cast<float>(value) / SCALE; }

    FixedPoint operator+(const FixedPoint &other) const {
        return fromRaw(value + other.value);
    }
    FixedPoint operator-(const FixedPoint &other) const {
        return fromRaw(value - other.value);
    }
    FixedPoint operator*(const FixedPoint &other) const {
        WideType prod = static_cast<WideType>(value) * other.value;
        return fromRaw(static_cast<BaseType>(prod >> FRAC_BITS));
    }
    FixedPoint operator*(float factor) const {
        return FixedPoint(toFloat() * factor);
    }

    friend std::ostream &operator<<(std::ostream &os, const FixedPoint &fp) {
        return os << fp.toFloat();
    }
};
```
The template parameters of this class are the split ratio of the underlying
fixed point type. This is fixed at compiler time for an instance of the type.
For example, `FixedPoint<8,16>` would mean the underlying type is a 16 bit
integer (`int16_t`) and the scale value would be `2^8` (`1 << 8`). Additionally,
for convenience, we implement addition, substraction and multiplication.
The central idea that this class makes apparent is all *operations* are
performed on the integer directly and *conversion* involves scaling and
de-scaling with the scale value that stays constant.

We can now introduce the division algorithm in its entirety:

```
using Fx8_16 = FixedPoint<8, 16>;
using Fx16_32 = FixedPoint<16, 32>;

Fx8_16 fxdiv_corrected(int n, int d) {
    assert(d != 0 && "Divide by zero undefined");

    if (n == 0) return Fx8_16(0.0f);

    bool result_is_negative = ((n < 0) != (d < 0));
    uint32_t nv = static_cast<uint32_t>(std::abs(n));
    uint32_t dv = static_cast<uint32_t>(std::abs(d));

    // 1. Normalization/scaling 'd' to fit between 0.5 and 1.0
    int shift = std::countl_zero<uint32_t>(dv);
    uint32_t scaled_val_raw = dv << shift;
    uint32_t scaled_val_n_raw = nv << shift;
    constexpr int INTERPRETATION_SHIFT = 31 - 16;

    Fx16_32 d_scaled = Fx16_32::fromRaw(static_cast<int32_t>(scaled_val_raw >> INTERPRETATION_SHIFT));
    Fx16_32 n_scaled = Fx16_32::fromRaw(static_cast<int32_t>(scaled_val_n_raw >> INTERPRETATION_SHIFT));

    // 2. Initial approximate calculation
    Fx16_32 a {2.8235294f}; // 48/17
    Fx16_32 b {1.8823529f}; // 32/17
    Fx16_32 initial_approx = a - (b * d_scaled);

    // 3. Newton-Raphson iterations
    Fx16_32 val = initial_approx;
    val = val * (Fx16_32{2.f} - (d_scaled * val)); // E1
    val = val * (Fx16_32{2.f} - (d_scaled * val)); // E2
    val = val * (Fx16_32{2.f} - (d_scaled * val)); // E3
    val = val * (Fx16_32{2.f} - (d_scaled * val)); // E4

    // 4. Multiplication with Numerator
    Fx16_32 res_16_32 = n_scaled * val;

    if (result_is_negative) {
        // Simple negation (assumes FixedPoint has a working negation operator or multiply by -1)
        res_16_32 = res_16_32 * -1.0f;
    }

    // Truncate from Fx16_32 (FRAC_BITS=16) to Fx8_16 (FRAC_BITS=8)
    constexpr int TRUNCATION_SHIFT = 16 - 8;

    // Shift the raw 32-bit value right by 8 bits to change the binary point position
    int32_t raw_final_32 = res_16_32.raw();
    int16_t raw_final_16 = static_cast<int16_t>(raw_final_32 >> TRUNCATION_SHIFT);

    Fx8_16 final_res = Fx8_16::fromRaw(raw_final_16);

    return final_res;
}
```

The algorithm had 4 parts: Normalization, Initial Approximation, NR Iterations,
Multiplication with Numerator. These are quite evident in the function above.
For intermidiate calculations, we use `FixedPoint<16,32>`, final results are in
`FixedPoint<8,16>`. There's something peculiar and previously un-explained in
this code: `INTERPRETATION_SHIFT` and `TRUNCATION_SHIFT`. These are there to
account for **correctly lining up the decimal points** at the start and the end
of the calculation.

The **INTERPRETATION_SHIFT** fixes the input value. When the divisor D is
normalized, the number is secretly set up with 31 digits after the decimal
(Q1.31). Since our math is being done in the Q15.16 format (only 16 digits after
the decimal), we have to move the value's decimal point to the left by **15
positions** (31 - 16). This right-shift makes sure the normalized input is read
as a number between 0.5 and 1.0, not as a very large integer.

The **TRUNCATION_SHIFT** manages the final output. The math produces a
high-precision number in the Q15.16 format. But the function needs to return the
result in the lower precision Q7.8 format (8 fractional bits). To shrink the
result to fit, we must move the decimal point left by **8 positions** (16 - 8).
This right-shift throws away the extra low-precision bits so the result matches
the final output type.

Let's compile and run this on an example:

```cpp
int main() {
    std::cout.precision(10);
    int n = 3;
    int d = 4;
    Fx8_16 result = fxdiv_corrected(n, d);
    std::cout << "Approximate division of " << n << "/" << d << ": " << result << std::endl;
    std::cout << "Real division of " << n << "/" << d << ": " << static_cast<float>(3)/static_cast<float>(4) << std::endl;
    return 0;
}
```

```bash
$ clang++ fixed_div.cpp -o a -std=c++20
$ ./a
Approximate division of 3/4: 0.74609375
Real division of 3/4: 0.75
```
Voila! 3 divided by 4 by our method results in `0.74609375` which is not that
far from the actual answer of `0.75`.

## Optimizations

What has been implemented is quite reasonable, but it can be optimized further. 

1.  Power-of-Two Denominator Shortcut

When the denominator d is a power of two (+/- 2^k), the division N/D simplifies
to a bit shift. This avoids the entire costly iterative Newton-Raphson loop.
Detecting if an integer is a power of 2 can be done in constant time. One can
put this check right at the top of the function an drastically speed up
power-of-two divisions.

2. Exploiting quadratic convergence and fraction length of resultant's type.

One property of NR iteration is **Quadratic Convergence**. In lay terms, every
iteration of the invocation of the Newton-Raphson formula, the number of correct
bits in the result roughly double. After first iteration, 2 bits are correct,
after second, 4, after third 8. Thus we have a rough idea of how many iterations
would be required for a given type. The optimization here is to skip NR
iterations on the basis of FRACTION_LENGTH of the resultant type. We can use
[constexpr if](https://en.cppreference.com/w/cpp/language/if.html) statements to
make sure the checks for type length do not affect runtime performance.

3. Using a different method to find initial approximation.

The [Remex algorithm](https://en.wikipedia.org/wiki/Remez_algorithm) can, in
theory, generate better approximations using a higher-degree polynomial. The
tradeoff in this case would be extra cycles to calculate the initial
approximation at the benefit of not having to do as many NR iterations.

There are many more that I've missed out. Recent
[research](https://dl.acm.org/doi/pdf/10.1145/3708472) propose optimization to
the chebyshev approximation method that we used above using look-up tables and
magic constants. Moreover, alternative methods such as
[CORDIC](https://en.wikipedia.org/wiki/CORDIC) can also be tried.

## Conclusion

This article came into being after I spent around a month trying to understand
approximation methods and getting code for it to work. The actual code was
contributed to the [llvm-project](https://github.com/llvm/llvm-project/) as an
addition to the stdfix library in the llvm libc project. Here is the
[PR](https://github.com/llvm/llvm-project/pull/154914).
[Here's](https://github.com/llvm/llvm-project/blob/7eee67202378932d03331ad04e7d07ed4d988381/libc/src/__support/fixed_point/fx_bits.h#L242)
a link to the complete division function implemented with stdfix primitives and
the optimizations mentioned above.
