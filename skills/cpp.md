# Modern C++ (C++17/C++20) Skill Standards

## 1. Memory Management & Smart Pointers
* Never use raw dynamic allocation keywords (`new` / `delete`).
* Manage dynamic lifetimes using smart pointers (`std::unique_ptr`, `std::shared_ptr`, `std::weak_ptr`).
* Use `std::make_unique` and `std::make_shared` for exception-safe memory allocation.
* Pass objects by reference to const (`const T&`) to avoid unnecessary object copying overhead.

## 2. RAII & Resource Safety
* Follow the RAII (Resource Acquisition Is Initialization) pattern strictly for all resource handles (files, sockets, mutexes).
* Manage mutex locking exclusively using `std::lock_guard` or `std::unique_lock`.
* Ensure destructor methods never throw exceptions; mark destructors `noexcept`.

## 3. Modern C++ Standard Features
* Target C++17 or C++20 standard capabilities.
* Use `auto` for variable declarations where type names are redundant or complex (e.g., iterators).
* Use `std::optional<T>` instead of returning raw fallback values or magic null pointers.
* Use `std::variant<Ts...>` for type-safe type unions instead of C-style unions.
* Use `std::string_view` for non-owning read-only string parameter views.

## 4. Class Design & Rule Guidelines
* Adhere strictly to the Rule of Zero, Rule of Three, or Rule of Five.
* Explicitly mark single-argument constructors as `explicit` to prevent unintended implicit type conversions.
* Declare member functions that do not modify class state as `const`.
* Use `override` keyword explicitly on overridden virtual functions in derived classes.

## 5. Type System & Casting
* Never use C-style type casts `(Type)var`.
* Use explicit C++ dynamic casting operators: `static_cast`, `reinterpret_cast`, `const_cast`, `dynamic_cast`.
* Avoid `reinterpret_cast` unless writing low-level hardware or binary serialization routines.

## 6. Standard Template Library (STL)
* Prefer STL algorithms (`std::transform`, `std::find_if`, `std::accumulate`) over manual `for` loops.
* Use ranges and views from `std::ranges` (C++20) for composable pipeline operations.
* Use `std::vector` as default sequence container; avoid fixed C-style arrays (`T arr[]`).

## 7. Error Handling Strategy
* Use exception classes inheriting from `std::exception` for exceptional error states.
* Mark non-throwing functions explicitly with the `noexcept` specifier to assist compiler optimizations.
* Use error codes (`std::error_code`) or outcome wrappers in low-latency performance-critical paths.

## 8. Concurrency & Threading
* Use standard thread abstraction primitives: `std::thread`, `std::jthread` (C++20), and `std::async`.
* Protect shared mutable data using atomic variables (`std::atomic<T>`) for lock-free operations.
* Avoid deadlocks by locking multiple mutexes simultaneously using `std::scoped_lock`.

## 9. Compilation & Code Organization
* Separate class interface declarations (`.hpp` / `.h`) from implementation details (`.cpp`).
* Enforce header guards using `#pragma once`.
* Organize project compilation workflows using CMake (`CMakeLists.txt`).

## 10. Performance & Optimization
* Utilize move semantics (`std::move`, `std::forward`) to avoid expensive deep copies.
* Enable high compiler optimization levels (`-O2` / `-O3`) and clean diagnostic flags (`-Wall -Wextra`).
