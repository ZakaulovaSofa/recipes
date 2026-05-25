import clsx from 'clsx';
import Link from '@docusaurus/Link';
import Heading from '@theme/Heading';
import Layout from '@theme/Layout';

import styles from './index.module.css';

function HomepageHeader() {
    return (
        <header className={clsx('hero hero--primary', styles.heroBanner)}>
            <div className="container">
                <Heading as="h1" className="hero__title">
                    Be cooking
                </Heading>

                <p className="hero__subtitle">
                    Документация веб-платформы онлайн-кулинарной книги
                </p>

                <div className={styles.buttons}>
                    <Link
                        className="button button--secondary button--lg"
                        to="/intro">
                        Открыть документацию
                    </Link>
                </div>
            </div>
        </header>
    );
}

export default function Home() {
    return (
        <Layout
            title="Be cooking"
            description="Документация проекта Be cooking">
            <HomepageHeader />

            <main>
                <section className={styles.section}>
                    <div className="container">
                        <div className="row">
                            <div className="col col--4">
                                <div className={styles.card}>
                                    <h2>Архитектура</h2>
                                    <p>
                                        Описание структуры Flask-приложения, HTML-интерфейса,
                                        REST API слоя, ролей и доступа.
                                    </p>
                                    <Link to="/architecture/overview">
                                        Перейти к архитектуре →
                                    </Link>
                                </div>
                            </div>

                            <div className="col col--4">
                                <div className={styles.card}>
                                    <h2>База данных</h2>
                                    <p>
                                        ERD, описание ORM-моделей, связей и логики хранения данных.
                                    </p>
                                    <Link to="/database/erd">
                                        Посмотреть ERD →
                                    </Link>
                                </div>
                            </div>

                            <div className="col col--4">
                                <div className={styles.card}>
                                    <h2>REST API</h2>
                                    <p>
                                        OpenAPI-спецификация и описание JSON-эндпоинтов для рецептов.
                                    </p>
                                    <Link to="/api/overview">
                                        Открыть API →
                                    </Link>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
            </main>
        </Layout>
    );
}