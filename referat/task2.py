import matplotlib.pyplot as plt


def optimize(method, x_init, gradient_fn, target_fn, learning_rate=0.1, iterations=1000):
    x = x_init  
    history = []


    momentum = 0
    grad_squared = 0
    rprop_grad_prev = 0
    rprop_step = 0.1
    v = 0
    m = 0
    rho = 0.9
    beta1, beta2 = 0.9, 0.999
    epsilon = 1e-8

    for t in range(1, iterations + 1):
        grad = gradient_fn(x)
        history.append(target_fn(x))

        if method == "SGD":
            x -= learning_rate * grad

        elif method == "Momentum":
            momentum = rho * momentum - learning_rate * grad
            x += momentum

        elif method == "QuickProp":
            if grad != 0:
                x -= grad / (abs(grad) + epsilon) * learning_rate

        elif method == "RProp":
            sign_change = (rprop_grad_prev * grad) > 0
            if sign_change:
                rprop_step *= 1.2
            else:
                rprop_step *= 0.5
            rprop_grad_prev = grad
            x -= rprop_step * (1 if grad > 0 else -1)

        elif method == "ConjugateGradient":
            x -= learning_rate * grad

        elif method == "NAG":
            lookahead = x + rho * momentum
            momentum = rho * momentum - learning_rate * gradient_fn(lookahead)
            x += momentum

        elif method == "AdaGrad":
            grad_squared += grad**2
            adjusted_lr = learning_rate / ((grad_squared**0.5) + epsilon)
            x -= adjusted_lr * grad

        elif method == "AdaDelta":
            grad_squared = rho * grad_squared + (1 - rho) * grad**2
            delta_x = -(v**0.5 + epsilon) / ((grad_squared**0.5) + epsilon) * grad
            v = rho * v + (1 - rho) * delta_x**2
            x += delta_x

        elif method == "Adam":
            m = beta1 * m + (1 - beta1) * grad
            v = beta2 * v + (1 - beta2) * grad**2
            m_hat = m / (1 - beta1**t)
            v_hat = v / (1 - beta2**t)
            x -= learning_rate * m_hat / ((v_hat**0.5) + epsilon)

        else:
            raise ValueError(f"Unknown method: {method}")

    return history


def plot_results(histories, methods):
    plt.figure(figsize=(10, 6))
    for history, method in zip(histories, methods):
        plt.plot(history, label=method)
    plt.xlabel("Итерации")
    plt.ylabel("Значение функции")
    plt.title("Сравнение градиентных методов")
    plt.legend()
    plt.grid()
    plt.show()


if __name__ == "__main__":
   
    def target_function(x):
        return x**2

    def gradient_function(x):
        return 2 * x

    x_init = 0.5 # Начальная точка
    methods = ["SGD", "Momentum", "QuickProp", "RProp", "ConjugateGradient", "NAG", "AdaGrad", "AdaDelta", "Adam"]
    learning_rate = 0.1
    iterations = 100

    # Сравнение методов
    histories = []
    for method in methods:
        try:
            history = optimize(method, x_init, gradient_function, target_function, learning_rate, iterations)
            histories.append(history)
        except Exception as e:
            print(f"Ошибка в методе {method}: {e}")

    # Построение графиков
    plot_results(histories, methods)